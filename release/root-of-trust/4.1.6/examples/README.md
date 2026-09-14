# Examples

| Directory / file | Revision | Status |
|---|---|---|
| `make_example.py`, `release-statement.payload.example.json`, `release.dsse.example.json`, `rev2/` | 2 | **Superseded by revision 3 and not regenerated.** They illustrate revision-2 statement shapes: `artifact-final.v1` under `release-final`, `historical-identity.v1`, TPS `floors[]`, TSS without `prior_states`, lock 2.0.0 with sentinels. They are not valid against the revision-3 schemas, and no revision-3 binary accepts those payloadTypes (`05` §2, `13` §9). They are kept for history. `examples/rev2/release-final.dsse.json` and `trust-state.1.dsse.json` are used by `evidence/P3r3` only as opaque stand-in files inside `governance/trust/`, which pre-RoT binaries never read. |
| `rev3/` | 3 | Schema-validated instances of the records revision 3 adds: Trust Base Manifest, build attestation, state pin, trust-gate confirmation, lock 3.0.0, FORMAT. `rev3/validation.json` records their validation. Illustrative only: no key, signature or ceremony is real. |

The machine-readable artefacts of revision 3 that carry evidence are in `../constitutional-surface/` (inventory and
checker) and `../evidence/` (P1r3, P3r3, P4r3, G1, CSI results).
