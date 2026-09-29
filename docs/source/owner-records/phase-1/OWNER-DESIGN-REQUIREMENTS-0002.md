# OWNER-DESIGN-REQUIREMENTS-0002 — Product-owner resolutions of OT-1 and OT-2 for CP-1 / Revision 7

| Field | Value |
|---|---|
| Record | OWNER-DESIGN-REQUIREMENTS-0002 |
| Source | the product owner, in the Phase 1 orchestration chat, 2026-09-14, after the orchestrator reported the architect-surfaced conflicts OT-1 and OT-2 of RoT-1 revision 7 (`d07d200`) |
| Classification | **binding owner resolutions** that clarify the already-selected OP-7, OP-10 and OP-13 requirements of OWNER-DESIGN-REQUIREMENTS-0001 |
| Not | activation, approval or ratification of D-0008 |
| D-0008 | remains `PROVISIONAL`, `PROPOSED`, `human_approved: false` until independent architecture acceptance and formal ratification |
| Effect on review | OT-1 and OT-2 are treated as resolved owner requirements. Reviewer B, reviewer C and the synthesis reviewer attack the resulting concrete design. Return to the owner only for a genuinely different security or product trade-off, not an implementation difficulty. |
| Recorded by | the Phase 1 orchestrator. The text below is the owner's message **verbatim** and is authoritative. |

## Verbatim owner text

```text
Record the following as PRODUCT-OWNER resolutions for CP-1 / Revision 7.

These clarify the already-selected OP-7, OP-10 and OP-13 requirements. They do not activate D-0008.

OT-1 — offline media versus 24-hour freshness

Resolve OT-1 as follows:

Do not extend or weaken the 24-hour freshness requirement for first admission.

The architecture must distinguish:

A. Immutable first-contact material

The two OP-13(b) channels must independently provide matching immutable material sufficient to establish:

- root lineage;
- trust-root fingerprints/identity;
- admitter identity and digest;
- Trust Base Manifest identity;
- compiled/bootstrap policy identity;
- other immutable first-contact artefacts defined by the accepted architecture.

One channel may be offline immutable media under separate custody.

The offline medium is therefore a second independent source of identity/authenticity, not a source of indefinite trust-state freshness.

B. Current trust state

Current trust-state/currency evidence remains subject to OP-7(a).

For production admission/install/update:

- the required trust-state anchor must satisfy the existing 24-hour freshness requirement;
- offline media receives no special longer freshness window;
- stale trust state on otherwise authentic media cannot become current merely because the medium is trusted;
- the machine's previously known trust high-water can never be lowered.

If fresh trust-state evidence is unavailable:

- first-contact immutable material may still be inspected/validated;
- the machine may operate only at the architecture's bounded diagnostic/bootstrap level;
- it must NOT complete governed production admission/install or enter C1-C3 based on stale state.

Thus:

offline source establishes independent first-contact identity; freshness is a separate property and remains fail-closed.

Do not introduce a clock-based grace-period exception.

If the reviewers find a technical reason why the immutable material itself requires a freshness property, distinguish that explicitly from mutable trust-state freshness rather than weakening OP-7.

---

OT-2 — compiler/toolchain assurance

Resolve OT-2 as follows:

No interim certification exception.

Keep all targets:

"NOT CERTIFIED"

until the OP-10(b) compiler/toolchain assurance criterion is evidenced.

Do not silently fall back to trusting the official upstream compiler archive.

However, refine the acceptance criterion so that its security objective is precise.

The objective of OP-10(b) is to prevent a compromised compiler/toolchain from reproducing malicious behaviour through otherwise reproducible builds — i.e. the trusting-trust class.

The architect and independent reviewers should define a practical evidence route using techniques such as:

- independently derived compiler provenance;
- diverse double compilation or an equivalent trust-breaking procedure;
- independent bootstrap chains where feasible;
- cryptographically registered toolchain inputs;
- multiple independent builders/reproducers;
- reproducible final artefacts;
- provenance evidence demonstrating that the purported diversity is genuine rather than different labels over the same bootstrap lineage.

Do NOT accept "two different distributions" or "two mirrors of the same compiler binary" as independence.

Likewise, do not require byte-identical output from fundamentally different compilers merely as a ritual if that is not the correct security test.

The acceptance condition should instead prove, with independent evidence, that the final trusted compiler/binary chain is not solely dependent on an unaudited upstream compiler binary being honest.

If satisfying this requirement for a particular Rust/platform target is not currently achievable, that target remains:

"NOT CERTIFIED — TOOLCHAIN ASSURANCE INCOMPLETE"

rather than weakening the Governance OS trust model.

This is acceptable for Phase 1 architecture acceptance: the architecture can be accepted even if no platform is yet production-CERTIFIED, provided the certification criterion is explicit, executable/testable and non-circular.

---

Effect on Revision 7 review

Treat OT-1 and OT-2 as resolved owner requirements.

Reviewer B, Reviewer C and the synthesis reviewer should now attack the resulting concrete design rather than treating these as unresolved choices.

Only return to the product owner if they discover a genuinely different security/product trade-off, not merely an implementation difficulty.

D-0008 remains:

- PROVISIONAL;
- PROPOSED;
- "human_approved: false";

until the architecture receives independent acceptance and the final D-0008 package is formally presented for ratification.
```
