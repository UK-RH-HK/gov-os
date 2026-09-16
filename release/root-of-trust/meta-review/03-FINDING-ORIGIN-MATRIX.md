# Finding-origin matrix

## Classification keys

- `O-N`: original baseline normative.
- `PO-N`: owner-added normative (Contract v3 or explicit owner record).
- `N-D`: technically necessary to make a normative guarantee true.
- `I-C`: implementation choice, not a product requirement.
- `V-H`: verifier hardening.
- `ODR`: new owner decision required.
- `L-Q`: later qualification/certification.
- `OOS`: out of scope or unsatisfiable as stated.

“Current owner-approved” includes Contract v3 and OWNER-DESIGN-REQUIREMENTS-0001/0002. It does not mean D-0008 itself is approved.

| Requirement / finding class | Original baseline? | Current owner-approved? | Provenance | Phase-1 disposition |
|---|---:|---:|---|---|
| Immutable releases, manifest, file hashes, version, migration and rollback | yes | yes | O-N | required |
| Independent release verification and held-out tests | yes | yes | O-N | required, proportionate to candidate stage |
| Framework/kernel separate from project overlay | yes | yes | O-N | required |
| Higher authority cannot be weakened by project/retrieved/model input | yes | yes | O-N | required |
| Secret/sensitivity and outbound default-deny boundaries | yes | yes | O-N | required |
| Source/release authenticity before privileged staging/install | no | yes (A2) | PO-N | required |
| Integrity and authenticity are separate | implicit only | yes (A2) | PO-N / N-D | required |
| Source directory cannot regenerate its trusted identity | no | yes (A2) | PO-N | required |
| One trust root covers init/adopt/update/reinstall/recovery/rollback | no | yes (A2) | PO-N | required at the guarantee level, not one mandatory implementation |
| Key rotation/revocation/recovery | no | yes (A2) | PO-N | architecture required; operational qualification later |
| Offline verification after authentic envelope where designed | no | yes (A2) | PO-N | conditional requirement; cannot imply current revocation knowledge offline |
| Plugin descriptors cannot self-authorize; byte-bound registry | derived from baseline | yes (F4) | PO-N / N-D | required |
| G0–G6 health scheduler | no | yes (O5) | PO-N | required to the maturity stated for each lifecycle |
| Qualification hidden oracle | no | yes (V) | PO-N | L-Q; format before qualification, full proof later |
| Gate W dependency consumption/lineage | partially (graph/context/task contracts) | yes | PO-N | required capability baseline; exhaustive scoring later |
| Three offline root keys, 2-of-3 | no | yes (OP-1) | PO-N | binding only while OP record remains; owner decision to simplify |
| Delegated registration quorum 2-of-3 | no | yes (OP-2) | PO-N | binding only while OP record remains |
| Always local trust gate | original human-gate concept only | yes (OP-3) | PO-N | required for listed operations; headless CI needs decision |
| Separate candidate, registration, state, certification, revocation and profile purposes | no | yes (OP-4) | PO-N | domain separation required; exact key topology is design-specific |
| 30-day informational metadata warning | no | yes (OP-5) | PO-N | non-security UX requirement |
| Once-per-machine lineage confirmation | no | yes (OP-6) | PO-N | current design requirement |
| 90d/7d anchors and 24h production state freshness | no | yes (OP-7, OT-1) | PO-N | current requirement; availability/currency boundary must be explicit |
| Two independent verifier records | original independence broadly | yes (OP-8) | PO-N | certification evidence, not release authenticity by itself |
| 2-of-3 independent reproducers plus registered final digests | no | yes (OP-9) | PO-N | L-Q unless owner insists on Phase-1 platform certification |
| Diverse independently bootstrapped compiler assurance | no | yes (OP-10, OT-2) | PO-N | L-Q; architecture may be accepted while all targets remain not certified |
| Raise minimum release sequence on security change | no | yes (OP-11) | PO-N | rollback protection required |
| Separate compiled first-install admitter | no | yes (OP-12) | PO-N / I-C | owner decision required to replace with standard bootstrap |
| Two separately custodied first-contact sources, both match | no | yes (OP-13) | PO-N | operational certification; bootstrap trust still external |
| Expiring admission and monotonic high-water | no | yes (OP-14) | PO-N | required if admission model retained |
| Revoked binary read-only only | no | yes (OP-15) | PO-N | required if revocation model retained |
| Two independent supplier classes | no | yes (OP-16) | PO-N | L-Q/platform certification |
| Full supplier × toolchain cross-product builds | no | no literal requirement | N-D only if claiming all cross-axis compromise bounds; otherwise I-C/V-H | do not make generic Phase-1 blocker |
| Complete selector/establishing-party register over every schema field | no | no, except D-0008 proposal | I-C/V-H | do not freeze as product requirement |
| Custom C0/C1/C2/C3 operation calculus | no | no | I-C | replaceable implementation |
| Every release fact current under repository/transport compromise without fresh information | no | no | OOS | impossible; state conditional guarantee |
| Prove genuine organizational independence from labels alone | no | owner rejects labels as proof | N-D | evidence/attestation required; absolute proof unavailable |

## Revision 7 consolidated findings

| Finding | Original? | Owner-approved? | Provenance | Reclassified Phase-1 disposition |
|---|---:|---:|---|---|
| RV7-H1 restrictive facts depend on unbounded Trust State listing | no | yes via OP-4/7/11/14/15 | N-D | valid blocker **for CP-1**; not a generic requirement for a smaller signed-release design |
| RV7-H2 C3 proof can name arbitrarily old state | no | yes via OP-7 and OT-1 | N-D | valid blocker **for CP-1**; solve by bounding signed metadata age or narrowing the promise |
| RV7-M1 one onboarding record designates both sources | no | yes via OP-13 | N-D / I-C | valid weakness in CP-1; exact remedy is a design choice and may need owner confirmation |
| RV7-M2 label-based independence; CC-3 not executable | no | yes via OP-10/16 and OT-2 | N-D, lifecycle L-Q | criterion must be executable before platform certification; should not block Phase-1 architecture if targets remain explicitly not certified |
| RV7-M3 cross-axis compromise outside stated bound | no | only broad OP-9/10/16 goals | N-D from CP-1's claimed bound; otherwise V-H | remove unsupported bound or test the matrix during qualification |
| RV7-M4 clean CI cannot reach claimed governed-use class | partial multi-machine baseline | no explicit resolution | ODR / availability | choose interactive/provisioned CI trust or exclude privileged CI; not a cryptographic blocker |
| RV7-M5 protected-store loss discards surviving high-water | no | yes OP-14 | N-D | implementation acceptance test if CP-1 retained |
| RV7-M6 no realizable per-project record identity | no | no exact mechanism | I-C | implementation design issue, not product requirement |
| RV7-M7 first-install journal-honouring unreachable | original rollback/recovery broadly | yes broadly | N-D at implementation level | implementation test, not reason to reject abstract source-auth architecture |
| RV7-M8 `git clean -fdx` defeats crash invariant | original recovery broadly | no exact promise | V-H / I-C | hardening or document administrative-destructive boundary |
| RV7-M9 roll-forward depends on in-memory ARO | original recovery broadly | yes broadly | N-D at implementation level | implementation test |
| RV7-M10 conformance vectors detect 14/22 mutants | no | Contract V later | V-H / L-Q | improve qualification suite; not architecture blocker |
| RV7-L1 schema allows threshold-1 root-held purposes | no | yes OP-1 | N-D | implementation/schema acceptance |
| RV7-L2 custodian without publication history can drop state | no | yes OP-7/13 | N-D for CP-1 | operational protocol qualification |
| RV7-L3 no state issuance/publication cadence | no | yes 24h guarantee | N-D | required only if claiming bounded current state |
| RV7-L4 stale/non-self-contained evidence runner | no | Contract evidence freshness | V-H / PO-N | evidence quality; refresh, not architecture redesign |
| RV7-L5 no genesis procedure for source-custodian verifier | no | yes OP-13 | N-D for CP-1 | bootstrap procedure qualification |
| RV7-L6 recovery undo/uninstall inconsistency | original recovery broadly | yes broadly | I-C/N-D | implementation test |
| RV7-L7 local wrong-ahead clock poisons high-water | no | OP-7 clock behavior | V-H / N-D | hardening; trusted-time limitations must be explicit |
| RV7-L8 high-water files lack atomicity | no | no exact mechanism | I-C | implementation test |
| RV7-L9 clock-reset replay/persistence unspecified | no | no literal requirement | I-C/V-H | implementation hardening |
| RV7-L10 air-gapped second-channel procedure unstated | no | yes OP-13/OT-1 | N-D | operational certification |
| RV7-L11 informational wildcard accepts future authority keys | baseline deny-lower-precedence generally | Contract A1 | N-D/V-H | schema-forward-compat test |
| RV7-L12 unflagged security change not listed | no | OP-11 broadly | N-D | implementation/certification test |
| RV7-I1 two verifier records only mechanically distinct | no | OP-8 | V-H / L-Q | organizational independence audit; cryptography cannot prove it alone |
| RV7-I2 ARCH-0002 lacks `human_approved` | no | state must remain unapproved | I-C | informational; `in_effect:false` is decisive |
| RV7-I3 OT-1 reading | no | yes | PO-N clarification | record in future owner package |
| RV7-I4 excluded-mode rows remain in history | no | owner requested exclusions from executable surface | V-H | documentation hygiene |
| RV7-I5 caller-declared role | original authority model assumed adapters | Contract A3/E1 | ODR / integration boundary | authenticate at deployment adapter where needed |
| RV7-I6 binding-group derivation | no | no literal requirement | I-C | informational |

## Matrix conclusion

The two HIGH Revision 7 findings are not reviewer goalpost movement: they falsify express CP-1/owner freshness and revocation claims. Several MEDIUM/LOW items are valid engineering concerns but were assigned to the wrong lifecycle. The correct response is phase separation, not another architecture revision.
