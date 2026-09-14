# 04 — Carried requirements (review r6 B)

This file turns the non-blocking findings into requirements that the implementation and the verifier must test.
- **Scope.** Each requirement tightens a rule the pack already states. Each test is independent of builder instrumentation.
- **Placement.** The synthesis reviewer decides whether any of them is instead an architecture change.

The last section lists the acceptance cases that a corrected design for the **blocking** findings (H1–H3) must pass. Those
are re-review entry cases, not carried requirements.

## Carried requirements

| ID | From | Requirement (normative for implementation) | Acceptance test |
|---|---|---|---|
| **CR6-B-01** | FC-R4, TB-S1 (environment) | Media under OP-13 (d) are prepared only from a first-contact manifest their custodian derived first-hand. Environment reproducers assemble only a manifest whose recipe and component selection are established (conditional on the H3 correction). | A media-provisioned machine whose media were written from a manifest naming a substituted admitter: the custodian's derivation step refuses before writing. RV6-B-A02 A07a on the implementation's environment tooling: refused before registration. |
| **CR6-B-02** | RV6-B-M1 | At re-admission (a store with an admission record exists), `gov-admit` applies the store's accepted-TBM high-water to the candidate (AP-8) and refuses a first-contact manifest whose state epoch is below the store's anchors. Alternatively, a running binary whose TBM is below the store's accepted-TBM high-water refuses above C0. `25` §7 and `31` §2 state which. | **(i)** RV6-B-A04 on `gov-admit`: after `ADMISSION_RECORD_EXPIRED`, re-admission of an older genuine published binary → `BINARY_T0_ROLLBACK`; nothing installed; no record written. **(ii)** The same after `BINARY_REVOKED_SELF` under OP-15 (a). **(iii)** RT-170 extended with both. |
| **CR6-B-03** | RV6-B-M2, RV6-B-M3 | **(a)** Calculator rendering never merges atoms of different classes (`repo` is never a reproducer key). `statements_check.py` S1 compares the atom sets behind each rendered set with the calculator's minimal sets, not only the text. **(b)** `register_check.py` completeness covers every statement field and manifest field that selects a value of a registered decision, and each names its establishing party and authority. | **(i)** The CONTENT block rows for USE print `repo` (or "repository writer"); a mutation of `compact()` that merges prefixes fails S1. **(ii)** A register mutation that removes the composer, submitter or manifest-author row fails C2. **(iii)** RT-183 gains both. |
| **CR6-B-04** | RV6-B-L1 | Security classification for R-CON-5 is carried as inventory data per unit (`security_classified: true`), covering at least `commands/COMMAND_CONTRACT.yaml` and `overlay-templates/*`, and any other unit the inventory marks security-relevant; not a name list in the checker. | RV6-B-A10 on the implementation: `registration-changes` on K1 (command contract) and K2 (tool-permission template) → exit 8; K3 (taxonomy comment) → exit 0 unless classified. |
| **CR6-B-05** | RV6-B-L2 | `05` §2 lists the revision-6 payload versions; `05` §1's `trust-state` row names the first-contact code. | Text review; RT-127. |
| **CR6-B-06** | RV6-B-L3 | The ceremony order and R-VER-1 name where a verifier's environment comes from before registration (the established manifest of the H3 correction), and verification records name the `environment_id` they reproduced in. | Text review; a verification attestation naming an unregistered environment is not counted. |
| **CR6-B-07** | RV6-B-L4 | R-CON-1's derivation is run with an admitted `gov` (or one built by the custodian from the registered source) and a checker from the registered source; pipeline-supplied tools are refused. | Ceremony record review; `draft-registration` refuses a derivation whose tool digest is not an admitted binary or the registered checker. |
| CR4-B-01, CR4-B-02, CR4-B-04, CR4-B-05 | review r4 | Still specification only in revision 6 (`22` §4); CR4-B-05 (RV4-L1): the wildcard `informational` rule still admits unknown keys (RV5-B-A09 CLS re-run byte-identical). | As review r4 B `04`. |

## Acceptance cases for corrected blocking findings (re-review entry)

| Finding | Case | Pass criterion |
|---|---|---|
| H1 | **(a)** RV6-B-A01 part P on the implementation: the process that composes Trust States and first-contact values is compromised; every source honest; under every OP-13 answer. **(b)** RV6-B-A01 part C on the corrected calculator with a composer atom for FA, P1, P2, CIR. | Every case is refused before any evaluator runs (a source's first-hand derivation disagrees), or the pack states the composer as a first-contact root atom with its computed sets and restates FC-ROOT, FC-KEY-THEFT, FC-CONTENT, OP-9-BYTES, `25` §7, OP-6 and OP-13. |
| H2 | **(a)** RV6-B-A05: an old genuine platform-signed package whose manifest has no `valid_until`, and one whose `valid_until` exceeds the compiled maximum. **(b)** RV6-B-A06: an honest signing service signing a submitter's substituted admitter. **(c)** FA6's platform-only branch using the package's own manifest. | (a) refused (`FIRST_CONTACT_MANIFEST_EXPIRED` or a missing-validity refusal); (b) refused, or the submitter is a stated root atom with computed sets; (c) the executed minima equal the corrected calculator's. |
| H3 | **(a)** RV6-B-A02 A07a, A07b, A07c, A08, A09 against the implementation's environment tooling and ceremony. **(b)** The corrected calculator with recipe, selection, label and upstream-key strategies. | (a) each refused before registration, or conflicting; (b) INV-ENV, INV-ENV-PIPELINE and INV-ENV-B hold with the strategies on, and the OP-16 block equals its output. |
