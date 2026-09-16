# Build supply-chain assessment

## Required separation

| Layer | Phase-1 minimum | Later qualification/certification |
|---|---|---|
| Source identity | pinned commit/tree/input manifest | protected branch/review provenance and source attestations |
| Build inputs | locked toolchain/dependencies and SBOM | independently reproduced input resolution |
| Build provenance | signed CI/build attestation bound to artifact digest | independent builders and policy evaluation |
| Artifact authenticity | authorized release signature over exact payload metadata | threshold/dual-control release promotion |
| Reproducibility | at least deterministic/repeatable build attempt where practical | 2-of-3 or other independent reproducibility quorum |
| Compiler trust | explicit toolchain identity and residual risk | DDC/equivalent independent bootstrap evidence |
| Environment diversity | declared environment identity | evidenced independent supplier classes and cross-axis tests where claimed |

## Assessment of OP-9, OP-10 and OP-16

These are legitimate owner-added high-assurance goals. They are not implied by the original framework and are not necessary to establish that a downloaded release was authorized by the Governance OS publisher.

The owner already supplied the correct phase distinction in OT-2: architecture acceptance is possible while no target is production-certified, provided the criterion is explicit, executable/testable and non-circular. Revision 7 failed even that narrower test because CC-3 relied on labels and lacked a practical procedure.

The meta-review recommends:

- keep the goals as a **platform certification profile**;
- mark every platform `NOT CERTIFIED — TOOLCHAIN ASSURANCE INCOMPLETE` until the evidence exists;
- do not block acceptance of the basic release-authentication architecture or non-production candidate on completion of DDC;
- use established attestation formats and policy engines rather than encoding build truth in custom release statements;
- state exactly which compromise combinations the evidence covers;
- do not infer supplier/toolchain independence from names.

## Revision 7 M2/M3 disposition

- RV7-M2 is a valid certification-criterion finding. It blocks claiming an OP-10/OP-16-certified target, not the entire Governance OS architecture.
- RV7-M3 is valid only against CP-1's stated compromise coverage. Either require an evidenced coverage matrix at qualification or narrow the claim. The full cross-product is not automatically a product requirement.

## Recommended evidence chain

For later certification:

1. source and dependency/input lock;
2. signed build provenance bound to exact artifact digest;
3. independent reproduction reports from genuinely separate infrastructure;
4. policy evaluation of identity, source, inputs and results;
5. optional DDC/equivalent toolchain evidence for high-assurance targets;
6. owner certification record referencing the evidence;
7. normal release-signing process publishes the certified artifact.

Build evidence informs eligibility/certification. It should not become the only root that lets a client authenticate the release metadata.
