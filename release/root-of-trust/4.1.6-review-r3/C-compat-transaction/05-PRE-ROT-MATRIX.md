# 05 — Pre-RoT command-register matrix (executed, independent)

## Method
A real 4.1.5 base project was built (init 4.1.4 → gated update to 4.1.5 → a `restricted` classification added to
`DATA_SENSITIVITY.yaml` *after* the update, matching review r2 P3), then transformed into the RoT-1 revision-3
legacy-path-occupation layout of `08` §2 / `26` §2 and committed as the migration commit on top of the legacy history.
The **real** binaries `gov-4.1.2`, `gov-4.1.3`, `gov-4.1.4`, `gov-4.1.5` were each run on a **fresh copy** of that
layout (`L3`) with a legacy update snapshot (`.governance-runtime/update/4.1.5/`) and the restricted classification
present. Whole-tree digests (recording entry TYPE, not only named paths) plus `governance/trust` and Git state were
captured before/after each run. Evidence: `evidence/run_destructive.py`, `evidence/destructive.json`.

This is an independent reproduction of the architect's `P3r3` property (its claim, not a finding), on a hand-built
layout and an independent destructive register. It is narrower than P3r3 (which drives each binary's full `--help`
register); it targets the destructive/state-changing subset the R2-H4 class turns on.

## Totals (L3, revision-3 layout, occupation intact)

| Binary | Destructive invocations | tree changed (excl .git/.governance-runtime) | governance/trust changed | git changed | classification lost |
|---|---|---|---|---|---|
| 4.1.2 | 21 | 0 | 0 | 0 | 0 |
| 4.1.3 | 21 | 0 | 0 | 0 | 0 |
| 4.1.4 | 21 | 0 | 0 | 0 | 0 |
| 4.1.5 | 21 | 0 | 0 | 0 | 0 |
| **Total** | **84** | **0** | **0** | **0** | **0** |

Refusal codes over the 84 runs: `NOT_INSTALLED` 49, `IO_ERROR` 16, no error code 19 (`resume`, and
`adopt/migrate rollback` restoring nothing). `ok:true` in 12 runs — all `adopt rollback` / `migrate rollback` that
restore nothing because the batch source `.governance-runtime/migration` is occupied.

**Property (independently reproduced):** on the intact revision-3 occupation layout, no real pre-RoT binary
4.1.2–4.1.5 writes a byte outside `.git/`+`.governance-runtime/`, changes Git state, or removes the restricted
classification. `governance/trust/**` is **never** in any legacy binary's write set (they only address
`governance/{kernel,project,generated,framework.lock}`, `spec/audits/GOVERNANCE-ADOPTION`, `.governance-runtime`),
so the new trust state is structurally outside their reach. This corroborates `P3r3` and closes RV2-A31…A36 for the
intact layout.

## Cross-check against the architect's P3r3 (claim under test)
`P3r3` reports 695 invocations + 40 chains, 0 changes on L3; L0 control 36–47 changing invocations per binary;
ablation L3A 4 changing invocations per binary (adopt/migrate baseline + batch-1 rollback). Reviewing the harness
(`evidence/P3r3-pre-rot-register-matrix.py`), the base construction, layout, whole-tree digests and control/ablation
are sound and match my independent construction. The one gap in P3r3's coverage — occupation-**absent** states — is
addressed in `01-FINDINGS.md` C-1 and `02-HELDOUT-ATTACKS.md` (RV3-C-A04…A06), not by P3r3.

## Environment
Linux 6.6 (WSL2), ext4 (`/dev/sdd`). RENAME_EXCHANGE / cross-device behaviour of the (unimplemented) RoT-1 install
transaction was reasoned from `18` §3, not executed — see `04-CARRIED-REQUIREMENTS.md` C-2.
