# OP-1…OP-16 disposition

These are current owner-approved design inputs. The dispositions below are recommendations only; changing them requires explicit owner action.

| OP | Current selection | Recommended disposition | Phase |
|---|---|---|---|
| OP-1 | 3 root keys, 2-of-3, separate offline custody | **Retain** as the offline root-policy target if operationally feasible | Phase 1 architecture; ceremony before production |
| OP-2 | 2-of-3 delegated registration | **Revise/simplify**: use delegated release-signing role with enforced dual-control promotion; cryptographic 2-of-3 optional profile | owner decision; production ops |
| OP-3 | always local gate | **Retain for interactive privileged lifecycle operations; clarify CI automation** | Phase 1 plus ODR for CI |
| OP-4 | extensive purpose separation and thresholds | **Retain domain separation; reduce key/statement topology to demonstrated needs** | Phase 1 core; advanced purposes later |
| OP-5 | 30-day warning only | **Retain** | operations/UX |
| OP-6 | confirm lineage once per machine | **Retain** as bootstrap UX where OS trust path is unavailable | Phase 1 |
| OP-7 | anchored-only, 90d/7d anchors, 24h production | **Revise to signed metadata expiry/refresh semantics and explicit stale mode; retain no-false-current rule** | owner decision because availability changes |
| OP-8 | two independent verification records | **Retain as release certification evidence, not distribution authenticity** | candidate/final certification |
| OP-9 | 2-of-3 reproducers + final digests | **Move to high-assurance platform certification** | later qualification/certification |
| OP-10 | diverse independently bootstrapped compiler | **Move to high-assurance platform certification; keep NOT CERTIFIED label until evidenced** | later certification |
| OP-11 | minimum sequence on every security change | **Retain rollback/security-minimum rule** | Phase 1 |
| OP-12 | separate compiled admitter | **Replace unless a concrete threat model justifies it**; use previously trusted verifier/installer or OS/admin trust bootstrap | owner decision |
| OP-13 | two owner-controlled sources, both match | **Retain as optional/high-assurance ceremony profile, not sole generic bootstrap** | later operational certification; owner decision |
| OP-14 | all admissions expire; preserve high-water | **Retain monotonic high-water; align expiry with signed metadata** | Phase 1 if admission concept retained |
| OP-15 | revoked binary read-only | **Retain** | Phase 1 recovery behavior |
| OP-16 | two supplier classes | **Move to high-assurance platform certification** | later certification |

## Cross-cutting owner inputs

| Input | Recommendation |
|---|---|
| First-contact composer/signer at root threshold | Retain only for the high-assurance ceremony profile; basic bootstrap still needs a pre-existing trusted root |
| Deterministically derived environment manifest | Retain as provenance evidence, not as the distribution root |
| Narrow initial certified targets | Retain; explicitly distinguish “candidate supported” from “high-assurance platform certified” |
| No fallback when assurance criterion absent | Retain: degrade or mark not certified; never silently weaken |

## Required owner decision package

The next owner gate should present:

- cost and operational burden of CP-1 versus the smaller target;
- which OP controls move from Phase 1 to platform certification;
- headless CI behavior;
- accepted bootstrap channels and local-admin assumptions;
- availability consequence of metadata expiry/freshness;
- whether the high-assurance CP-1 research profile remains a future product option.
