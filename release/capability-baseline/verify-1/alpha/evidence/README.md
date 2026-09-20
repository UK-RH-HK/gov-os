# P2-AR-0046 — evidence index (family alpha, verification iteration 1)

Every file here is the captured output of something this verification ran on `cap2-candidate-1`
(`0bad524d…`, `product_code_digest e6332fc7…`). Nothing here is copied from a builder, an integrator
or an iteration-0 audit.

| File | What produced it |
|---|---|
| `00-pinned-inputs.out` | the pinned-identity checks: tag commit, `product_identity.py` for HEAD and for the tag, the two SHA-256s, and a direct count of the alpha checklist bullets in the owner source (100) |
| `t01-a2-root-of-trust.out` | `heldout/t01_a2_root_of_trust.py` — A2 bullet by bullet |
| `t02-cross-machine.out` | `heldout/t02_cross_machine.py` — the five-machine cross-machine attack (S6, P2-ADJ-0002, OD-P2-02, SRR-R0-L4) |
| `t03-gate-a.out` | `heldout/t03_gate_a.py` — A1, A3, A4, A5 |
| `t04-adopt-roles.out` | `heldout/t04_adopt_roles.py` — S4 A0–A11, T1–T3, relocated OS stores, B2.3 |
| `t05-release-init-update.out` | `heldout/t05_release_init_update.py` — S1, S2, S3, S5 including the complete update lifecycle |
| `t06-gate-b-contract-freshness.out` | `heldout/t06_gate_b_contract_freshness.py` — B1–B3, the derived contract views, freshness |
| `t07-prior-findings.out` | `heldout/t07_prior_findings.py` — first-hand disposition of the remaining iteration-0 findings |
| `cargo-lib.out` | `cargo test --lib` in this worktree (regression evidence, O3) |
| `cargo-certification.out` | `cargo test --test certification` in this worktree — **207 passed, 0 failed** (regression evidence, O3) |
| `cargo-certification.timing-note.md` | why that suite landed after this report was first committed |

Re-run everything with `../heldout/RUN-ALL`. Each suite prints one `PASS`/`FAIL` line per check. The
checks that fail on this candidate are the findings in `../findings.yaml`; RUN-ALL exits non-zero
while any of them fails.

The signing side of every probe is `../heldout/lib/srrsign.py`, an independent metadata producer
written for this verification against the on-disk format, using python-`cryptography`'s ed25519 —
never the product's own `tests/certification/srr_material.rs`. Keys are drawn per run into a
throw-away administrator-domain directory outside every repository; none is committed.
