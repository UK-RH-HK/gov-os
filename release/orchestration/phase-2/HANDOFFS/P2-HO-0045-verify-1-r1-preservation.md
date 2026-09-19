# P2-HO-0045 — Verification iteration 1: AC-14 R1 preservation

| Field | Value |
|---|---|
| Handoff | P2-HO-0045 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent **R1-preservation verifier**, run **P2-AR-0044** |
| Candidate | `cap2-candidate-1` (identities in your dispatch message and `ORCHESTRATOR_STATE.yaml`) |
| Reference | `srr1-r1-accepted` (tag; `product_code_digest` `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547`) — `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` (AR-0033, `release/verification/4.1.6-r1-4/`) |
| Evidence directory | `release/capability-baseline/verify-1/r1-preservation/` |
| Required verdict | `R1_PRESERVED` or `R1_NOT_PRESERVED` (with the failing items), or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0043-verify-1-common-protocol.md`; the frozen gate contract AC-4, AC-14 and §9.3; the
frozen SRR boundary `release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` (SHA-256
`70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1`), its R1 section (lines 67–84); ARCH-0003; D-0007;
`release/orchestration/phase-1/HANDOFFS/HO-0033-r1-verification-4.md` ("Preservation — must still hold"); the AR-0033
verification report `release/verification/4.1.6-r1-4/00-VERIFICATION-REPORT.md`.

## What you establish

You do not re-issue `ROT_PHASE1_CANDIDATE_ACCEPTED_R1`. You record whether that acceptance **remains valid** for
`cap2-candidate-1`, whose product code differs from `srr1-r1-accepted` (frozen contract §9.3).

1. **Every prior R1 held-out suite, unedited.** `release/verification/4.1.6-r1{,-2,-3,-4}/evidence/heldout-tests/`, built
   against **this candidate** through a private, uniquely named path. Record byte identity of every suite file you ran and
   the file/function census the suites print. Compare with the recorded baselines (AR-0027 26/3; AR-0029 26/2 with
   `ho_f` not compiling; AR-0031 27/7; AR-0033 31/0 at candidate 4) and explain every difference. AR-0033
   `hv_a_derivation::a1` pins 84 files / 740 functions and fails on any larger tree: judge it **on its property** — run its
   census with only the size assertions removed in a labelled copy and report violations per §6 activity; also run
   AR-0033's `derive.py`.
2. **The twelve frozen R1 items for every changed area.** Diff `srr1-r1-accepted..cap2-candidate-1` over the product tree
   yourself and name every area that touches an R1 item (trust root and verifier, admission and install, staging/rollback/
   recovery, floors/high-water, D-0007 controls, lifecycle ingress, project/CLI/env/model/plugin trust inputs, CI and
   multi-machine provisioning, the original product controls and the G0–G6 / Gate W mappings). For each changed area,
   re-establish the affected items with your **own** held-out tests (`heldout/`), especially:
   - the new T2 binding authority (`srr/binding.rs`, `t2.rs`, `gov trust bind`/`reseal`): it is delegated from the
     provisioned root under ARCH-0003 §8, repository content cannot create it, and `gov` never signs;
   - `gov update` admission and rollback (`update.rs`, scheduler `admit`/`confirm_remedy`);
   - relocated OS stores and legacy relocation (`paths::store_path`, `relocate_legacy`) — no trusted state becomes
     writable by project content;
   - kernel payload/version consistency (KERNEL.yaml mirroring, `health` in the payload) and the embedded-payload bootstrap
     under OD-P2-02.
3. **HO-0033 structural invariants**: the four-operation §5 allow-list with exact-match semantics; five `admit` sites
   paired with five `install_kernel` sites; one `by_admit`; one `AuthenticatedRelease` literal; zero `Clearance`
   constructions outside `breakglass`; floors at all six ingresses, advancing last; transaction abort is not a bypass;
   D-0007 establishes **intact**, never **authentic** or **admissible**; `SRR-R0-L4` vacuous; Contract v3 canonical import
   byte-identical at `4c2df291…` and failing closed. Where a count changed, say whether the property still holds and why.
4. Regression: `cargo test --lib` and `cargo test --test certification` on the candidate, your own run.

Findings use the common protocol's schema (lifecycle labels per the frozen SRR boundary: R1/R2/R3/operations; R2/R3
concerns are never Phase-2 blockers — record them as later-lifecycle notes). Your run report verdict is one of the three
above; `R1_NOT_PRESERVED` lists each failing item with its evidence.
