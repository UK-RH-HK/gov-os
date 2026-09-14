# Output 34 — Registered constitutional content established first-hand (BC5-3)

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> New in revision 6. It closes blocking class **BC5-3** (review r5 RV5-H3) under rule FD-1 (`29`). The registered content of a
> release is derived first-hand by the registration authority. Verification is bound to exactly the registered candidate and
> kernel. E7 applies admission-predicate/1's restrictors, and registration reductions are computed at the verifier.
> Amended to match: `23` §12, `19` E7, `25` AP-4/AP-5, `30` R-REG-3, R-VER-1/2, R-PUB-1′, `04` V8, `05` §1. Closing it
> requires **no owner trade-off** (review r5 `11` CD5-3). Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

**Mistaken equivalence (revision 5):** *the registration authority signed the unit map ⇒ the registration authority
established it.*

| Revision-5 rule | What it let a lower-trust input do |
|---|---|
| `23` §12.5: canonical CI (`derive-registration`) produces the unit map; the ceremony lists differences | the pipeline chose the unit map and kernel tree digest that the custodians signed |
| R-REG-3 (d), R-VER-2, AP-5: ACCEPTED attestations "for this `source` and `inputs_manifest_digest`" | a verification of candidate C (kernel K_fix) was reused for a candidate C′ (kernel K_weak) with the same source |
| `19` E7 / `23` §12.3: registration referenced, final named, units and tree equal | no verification, candidate or revocation condition on the policy root |

RV5-D-A01 executed the route. The pipeline, plus the threshold-1 `release-candidate` and `release-final` keys (one everyday key
under OP-4 "no"), got a weakened `aws-access-key` regex registered and eligible. On the real 4.1.5 binary a temporary AWS key
file was then indexed and served. Under OP-2 (b), two delegated custodians plus `release-final` sufficed with no verification
compromise (RV5-B-H3).

## 2. Invariant

1. The effective constitutional content of a release is established first-hand at the registration's authority. That content
   is the kernel tree digest, every non-join unit value and every migration digest.
2. It is bound to OP-8 verification records for **exactly the registered candidate**. That candidate's kernel equals the
   registered kernel, and the registered final is promoted from it.
3. E7 (policy-root eligibility, at ingress and at use) applies the same restrictors as admission-predicate/1 AP-4 and AP-5.
4. No threshold-1 release key, alone or with pipeline input, selects content.

## 3. Rules (R-CON)

| ID | Rule | Refusal |
|---|---|---|
| **R-CON-1** | **First-hand derivation.** Each registration custodian (OP-2 (a) root custodian or (b) delegated custodian) builds the kernel payload from the source it fetched (`30` R-REG-3 (e)) with the registered input manifest, under the normative packaging profile (`gov release build --kernel-only`, deterministic). From that payload it derives the kernel tree digest, the unit map and the migration digests (`csi_check.py verify-registration --registration <proposal> --source-kernel <own build>`). It signs only when the proposal equals its derivation in every field. CI output is a proposal, never an input to the signature. | `REGISTRATION_CONTENT_NOT_ESTABLISHED` (checker exit 3; `draft-registration` refuses) |
| **R-CON-2** | **Verification bound to what is registered.** A `verification-attestation.v4+json` names `{candidate_statement_digest, verdict, source, inputs_manifest_digest, kernel_tree_digest}`. `kernel_tree_digest` is the digest of the kernel payload the verifier itself reproduced from the source (R-VER-1). R-REG-3 (d), R-VER-2 and AP-5 count an ACCEPTED attestation only when all four hold: its candidate is the registered candidate; its kernel tree digest is the registered one; it is listed by the registration; it is unrevoked. The registered final MUST be promoted from the registered candidate and carry the registered kernel tree digest. The registered candidate MUST carry the registered kernel tree digest and source. | `VERIFICATION_RECORDS_BELOW_MINIMUM` / `RELEASE_FINAL_UNVERIFIED` |
| **R-CON-3** | **E7 applies AP-5's restrictors.** A release R is an eligible policy root only if every condition below holds on the statements the machine holds, at ingress and at use. The registration of R is referenced by the effective TSS and not revoked. The registered final and candidate are held, verify, are not revoked, and the final is promoted from the registered candidate. Both carry the registered kernel tree digest and source. No held REJECTED attestation names the registered candidate, unless it is removed by the registration authority (AP-5r). At least OP-8 ACCEPTED attestations by distinct keys meet R-CON-2. | E7 reasons `registration_revoked`, `release_final_unverified`, `final_not_promoted_from_registered_candidate`, `kernel_tree_digest_mismatch`, `registered_candidate_unverified`, `candidate_kernel_or_source_mismatch`, `revoked`, `artifact_source_rejected`, `verification_records_below_minimum` |
| **R-CON-4** | **Reductions computed at the verifier** (CR5-B-04 (a)). At ingress and at use, the verifier computes registration reductions (`23` §12.4) over every registration the effective TSS references. If any referenced registration is not held, the result is `INCOMPLETE` and E7 refuses the release. An undeclared reduction refuses the release. | `registration_history_incomplete` (checker exit 7); `REGISTRATION_UNDECLARED_REDUCTION` (exit 6) |
| **R-CON-5** | **Changes listed per project** (CR5-B-04 (b), (c)). For non-orderable units only exact reversion, removal and member narrowing are computable reductions. Any other change of a security-classified non-orderable unit is selected by the registration authority. Such a change is listed in the per-project `registration_change` gate package on every machine whose per-project record holds an earlier registration, and security-relevant use of the new release waits for that gate. Security-classified units are those of the security, authority, gate, tool, role, hard-invariant, tool-registry and MCP-registry files (`csi_lib.SECURITY_CLASSIFIED_NAMES`). | checker exit 8 (listed); `REGISTRATION_CHANGE_GATE_REQUIRED` |
| **R-PUB-1′** | **The publisher applies E7's restrictors** before referencing a registration in `registrations[]`, on the statements it holds first-hand (`30` §8). It is defence in depth: the verifier-side R-CON-3 is load-bearing. | the publisher does not reference |

**What "down" means for non-orderable units** (D-0008 rule (6) as restated): a value equal to one an intermediate
registration superseded (reversion), a unit removed, or a member set narrowed against its direction. Every other difference
is a change the registration authority selects. It is never computed as safe, and R-CON-5 lists it before security-relevant
use on recorded machines.

## 4. Who selects content under each owner answer (computed)

Atoms: `rc` and `rf` are the `release-candidate` and `release-final` keys. `kc` is one everyday key holding both (OP-4 "no").
`cust`/`regk` are registration custodians and keys; `vp`/`va` are verification processes and keys. Victims: `USE` is use of a
Git-delivered release (C1–C2); `ING_P1` and `ING_P2k1` are ingress with a P1 proof or an in-gate fingerprint.

<!-- CS6:BEGIN CONTENT -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| OP-2 | OP-4 | OP-8 | Victim | Minimal sets: malicious non-orderable constitutional content effective |
|---|---|---|---|---|
| root | sep | 1 | USE | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, rc, rf}; {2 registration keys, 1 verification key, 1 reproducer key, pipeline, ts}; {2 registration keys, 1 verification key, 1 reproducer key, ts, rc, rf} |
| root | sep | 1 | ING_P1 | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, rc, rf} |
| root | sep | 1 | ING_P2k1 | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, rc, rf}; {2 registration keys, 1 verification key, pipeline, ts, ch1}; {2 registration keys, 1 verification key, ts, rc, rf, ch1} |
| root | sep | 2 | USE | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, rc, rf}; {2 registration keys, 2 verification keys, 1 reproducer key, pipeline, ts}; {2 registration keys, 2 verification keys, 1 reproducer key, ts, rc, rf} |
| root | sep | 2 | ING_P1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, rc, rf} |
| root | sep | 2 | ING_P2k1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, rc, rf}; {2 registration keys, 2 verification keys, pipeline, ts, ch1}; {2 registration keys, 2 verification keys, ts, rc, rf, ch1} |
| root | shared | 1 | USE | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, kc}; {2 registration keys, 1 verification key, 1 reproducer key, pipeline, ts}; {2 registration keys, 1 verification key, 1 reproducer key, ts, kc} |
| root | shared | 1 | ING_P1 | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, kc} |
| root | shared | 1 | ING_P2k1 | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, kc}; {2 registration keys, 1 verification key, pipeline, ts, ch1}; {2 registration keys, 1 verification key, ts, kc, ch1} |
| root | shared | 2 | USE | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, kc}; {2 registration keys, 2 verification keys, 1 reproducer key, pipeline, ts}; {2 registration keys, 2 verification keys, 1 reproducer key, ts, kc} |
| root | shared | 2 | ING_P1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, kc} |
| root | shared | 2 | ING_P2k1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, kc}; {2 registration keys, 2 verification keys, pipeline, ts, ch1}; {2 registration keys, 2 verification keys, ts, kc, ch1} |
| delegated | sep | 1 | USE | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, rc, rf}; {2 registration keys, 1 verification key, 1 reproducer key, pipeline, ts}; {2 registration keys, 1 verification key, 1 reproducer key, ts, rc, rf} |
| delegated | sep | 1 | ING_P1 | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, rc, rf} |
| delegated | sep | 1 | ING_P2k1 | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, rc, rf}; {2 registration keys, 1 verification key, pipeline, ts, ch1}; {2 registration keys, 1 verification key, ts, rc, rf, ch1} |
| delegated | sep | 2 | USE | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, rc, rf}; {2 registration keys, 2 verification keys, 1 reproducer key, pipeline, ts}; {2 registration keys, 2 verification keys, 1 reproducer key, ts, rc, rf} |
| delegated | sep | 2 | ING_P1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, rc, rf} |
| delegated | sep | 2 | ING_P2k1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, rc, rf}; {2 registration keys, 2 verification keys, pipeline, ts, ch1}; {2 registration keys, 2 verification keys, ts, rc, rf, ch1} |
| delegated | shared | 1 | USE | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, kc}; {2 registration keys, 1 verification key, 1 reproducer key, pipeline, ts}; {2 registration keys, 1 verification key, 1 reproducer key, ts, kc} |
| delegated | shared | 1 | ING_P1 | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, kc} |
| delegated | shared | 1 | ING_P2k1 | {insider}; {1 verification process, pipeline}; {2 registration custodians, 1 verification key, pipeline}; {2 registration custodians, 1 verification key, kc}; {2 registration keys, 1 verification key, pipeline, ts, ch1}; {2 registration keys, 1 verification key, ts, kc, ch1} |
| delegated | shared | 2 | USE | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, kc}; {2 registration keys, 2 verification keys, 1 reproducer key, pipeline, ts}; {2 registration keys, 2 verification keys, 1 reproducer key, ts, kc} |
| delegated | shared | 2 | ING_P1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, kc} |
| delegated | shared | 2 | ING_P2k1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, kc}; {2 registration keys, 2 verification keys, pipeline, ts, ch1}; {2 registration keys, 2 verification keys, ts, kc, ch1} |
<!-- CS6:END CONTENT -->

**Statements that follow from the computed sets** (every set above; checked by `decision-register/statements_check.py`):
- No set consists of `rc`, `rf`, `kc`, `pipeline`, `ts`, transport or repository atoms only (invariant INV-RF).
- Every set that is not a residual contains either (i) the registration threshold, as custodians or keys, with at least OP-8
  verification compromises, or (ii) pipeline input with at least OP-8 verification processes: route TB-4′ (INV-CONTENT).
- Under OP-2 (b) the delegated quorum, restricted by OP-8 verification, is the selector of content. This is a stated
  consequence of OP-2, not a new trade-off.
- OP-4 "no" adds no set.

On a first-admission machine the first-contact root also selects content (`32` §7):

<!-- CS6:BEGIN FC-CONTENT -->
| OP-13 answer | First-contact root sets for content on a first-admission machine |
|---|---|
| a | {ch1} |
| b | {ch1, ch2}; {ch1, op1src} |
| c_all_1 | {ch1, alt} |
| c_all_2 | {ch1, ch2, alt}; {ch1, op1src, alt} |
| c_either_1 | {ch1}; {alt} |
| c_either_2 | {alt}; {ch1, ch2}; {ch1, op1src} |
| d | {media} |
<!-- CS6:END FC-CONTENT -->

## 5. Forward compatibility (HO-0001 §4)

A new constitutional file shipped in a kernel (for example the Capability Acceptance Contract Markdown and compiled YAML) is
classified by inventory data (`23` §7.1). Its content is fixed per release by R-CON-1 like every other non-join unit, and its
effective value needs R-CON-3. RV5-I2 (derivation between members of an owner-domain binding group) is carried to the
capability-contract phase as RT-182.

## 6. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-4 (route I) | an insider change accepted by honest verification | process; OP-8 | — |
| TB-4′ (TA-11) | OP-8 compromised verification processes plus pipeline input | §4 sets | CS6 `G_CONTENT` |
| RA-1 | the registration authority at threshold with OP-8 verification compromises (OP-2 (a): root threshold, A8; (b): delegated quorum) | §4 sets; R-CON-5 lists non-reduction changes on recorded machines | CS6; CON6 |

## 7. Evidence

| Evidence | Kind | Result |
|---|---|---|
| `evidence/r6/CON6-first-hand-constitutional-content.{py,json}` part B (pack checker as amended; real legacy 4.1.5 as the consumer) | executed | RV5-D-A01: the ceremony refuses the CI-derived proposal (exit 3, kernel tree and the `aws-access-key` unit not established); signs the first-hand proposal (0); E7 refuses the attacker kernel under the only registration the ceremony signs (3); the genuine kernel is eligible (0); the genuine 4.1.8 regex change is listed for recorded projects (exit 8). RV5-B-A09: variant regex and tool command listed (8, 8). RV5-B-A10: undeclared reversion refused at the verifier (6); intermediate registration withheld `INCOMPLETE` (7). RV5-D-A05: N3 ceremony refuses the attacker contract (3); N4 E7 refuses it (3); N2 genuine (0). On 4.1.5 the content revision 6 makes effective keeps the `ASIA…` file out of index and query; the refused content indexes and serves it (harm control). 17/17 verdicts. |
| `evidence/r6/P4r6-conformance-oracle.{py,json}` section G | computed | RV5-D-A01 part A: attacker candidate and final (`verification_records_below_minimum`); a variant registration naming the attested candidate (`final_not_promoted_from_registered_candidate`); OP-4 "no" (`verification_records_below_minimum`); RV5-B-A06 registration without a verification record; held REJECTED; candidate not held; ceremony refusals for non-first-hand content, records for another candidate, a REJECTED record and non-first-hand records; the genuine release eligible |
| `constitutional-surface/csi_check.py selftest` S71–S77 | executed | `verify-registration` 0/3; `registration-reductions --verifier` 6 and 7 (INCOMPLETE); `registration-changes` 8 for a regex variant and a tool command, 0 for unchanged units |
| `evidence/r6/CS6-derivation-calculator.json` goal `G_CONTENT` | computed | INV-CONTENT and INV-RF hold in every configuration; rules `V_CANDIDATE_BINDING` and `V_E7_RESTRICTORS` load-bearing (mutation analysis) |
| `evidence/r6/DA03r6-oracle-regression-sensitivity.json` section 4 | computed | every revision-6 E7 and ceremony rule mutant detected |
