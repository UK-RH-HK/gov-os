# Output 34 — Registered constitutional content established first-hand (CP-1)

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 7** concretises this file to CP-1 (`35`): the registration authority is the 2-of-3 delegated quorum (OP-2 (b)),
> content needs two verification records (OP-8), the release-final key threshold is 2 (OP-4), attestations name their
> environments (RV6-L3), derivation tools are registered (RV6-L4, CR6-B-07), and the consequence block is CS7's for CP-1 with an
> injective renderer (RV6-M1). RV6-L1 (security classification as explicit per-unit inventory data) is carried with a named test
> (§3 R-CON-5, RT-198). New in revision 6 for BC5-3. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

**Mistaken equivalence (revision 5):** *the registration authority signed the unit map ⇒ the registration authority
established it.*

| Revision-5 rule | What it let a lower-trust input do |
|---|---|
| `23` §12.5: canonical CI produces the unit map; the ceremony lists differences | the pipeline chose the unit map and kernel tree digest that the custodians signed |
| R-REG-3 (d), R-VER-2, AP-5: ACCEPTED attestations "for this `source` and `inputs_manifest_digest`" | a verification of candidate C (kernel K_fix) was reused for a candidate C′ (kernel K_weak) with the same source |
| `19` E7 / `23` §12.3: registration referenced, final named, units and tree equal | no verification, candidate or revocation condition on the policy root |

RV5-D-A01 executed the route on the real 4.1.5 binary (a weakened `aws-access-key` regex registered and eligible; a temporary AWS
key file indexed and served). Revision 6 closed it; review r6 confirmed the closure at the registration (CD6-0).

## 2. Invariant

1. The effective constitutional content of a release (kernel tree digest, every non-join unit value, every migration digest) is
   established first-hand by 2 of 3 registration custodians.
2. It is bound to **two** verification records for exactly the registered candidate, whose kernel equals the registered kernel and
   from which the registered final (threshold 2) is promoted.
3. E7 (policy-root eligibility, at ingress and at use) applies the same restrictors as admission-predicate/1 AP-4 and AP-5.
4. No release key, alone or with pipeline input, selects content; neither does the release-final threshold with the candidate
   key without the registration threshold.

## 3. Rules (R-CON)

| ID | Rule | Refusal |
|---|---|---|
| **R-CON-1** | **First-hand derivation.** Each signing registration custodian builds the kernel payload from the source it fetched (`30` R-REG-3 (e)) with the registered input manifest, under the normative packaging profile (`gov release build --kernel-only`, deterministic), in its own derived environment. From that payload it derives the kernel tree digest, the unit map and the migration digests (`csi_check.py verify-registration --registration <proposal> --source-kernel <own build>`), using an admitted `gov` and the checker from the registered source (`33` R-BENV-9). It signs only when the proposal equals its derivation in every field. CI output is a proposal, never an input to the signature. | `REGISTRATION_CONTENT_NOT_ESTABLISHED` (checker exit 3); `DERIVATION_TOOL_UNREGISTERED` |
| **R-CON-2** | **Verification bound to what is registered.** A `verification-attestation.v5+json` names `{candidate_statement_digest, verdict, source, inputs_manifest_digest, kernel_tree_digest, environment_ids, toolchain_ids, verifier_execution_id, verification_report_digest}`. `kernel_tree_digest` is the digest of the kernel payload the verifier reproduced. R-REG-3 (d), R-VER-2′ and AP-5 count an ACCEPTED attestation only when its candidate and kernel are the registered ones, it names the registered environments, it is listed by the registration and unrevoked, and it is one of two from distinct keys, executions and reports. The registered final MUST be promoted from the registered candidate and carry the registered kernel tree digest; the registered candidate MUST carry the registered kernel tree digest and source. | `VERIFICATION_RECORDS_BELOW_MINIMUM` / `RELEASE_FINAL_UNVERIFIED` |
| **R-CON-3** | **E7 applies AP-5's restrictors.** A release R is an eligible policy root only if, on the statements the machine holds, at ingress and at use: the registration of R is referenced by the effective TSS and not revoked; the registered final and candidate are held, verify (final at threshold 2), are not revoked, and the final is promoted from the registered candidate; both carry the registered kernel tree digest and source; no held REJECTED attestation names the registered candidate (unless removed by the registration authority, AP-5r); two ACCEPTED attestations meet R-CON-2; R's sequence is at least the computed security minimum (`19` E3′). | E7 reasons `registration_revoked`, `release_final_unverified`, `final_not_promoted_from_registered_candidate`, `kernel_tree_digest_mismatch`, `registered_candidate_unverified`, `candidate_kernel_or_source_mismatch`, `revoked`, `artifact_source_rejected`, `verification_records_below_minimum`, `below_security_minimum` |
| **R-CON-4** | **Reductions computed at the verifier.** At ingress and at use, the verifier computes registration reductions (`23` §12.4) over every registration the effective TSS references. If any referenced registration is not held, the result is `INCOMPLETE` and E7 refuses the release. An undeclared reduction refuses the release. | `registration_history_incomplete` (checker exit 7); `REGISTRATION_UNDECLARED_REDUCTION` (exit 6) |
| **R-CON-5** | **Changes listed per project.** For non-orderable units only exact reversion, removal and member narrowing are computable reductions. Any other change of a security-classified non-orderable unit is selected by the registration authority; it is listed in the per-project `registration_change` gate package on every machine whose per-project record holds an earlier registration, and security-relevant use of the new release waits for that gate. A registration with such a change sets `security_relevant_change` (OP-11 (b)). **Carried (RV6-L1, CR6-B-04):** the classification is inventory data per unit: every non-orderable unit row MUST carry `security_classified` explicitly (at least `commands/COMMAND_CONTRACT.yaml` and `overlay-templates/*` true), and the checker MUST refuse a row without it. The revision-6 checker still falls back to a compiled name and prefix list; the implementation requirement and test are RT-198. | checker exit 8 (listed); `REGISTRATION_CHANGE_GATE_REQUIRED`; `INVENTORY_ROW_SECURITY_CLASSIFICATION_MISSING` (RT-198) |
| **R-PUB-1′** | **The publisher applies E7's restrictors** before referencing a registration in `registrations[]`, on the statements it holds first-hand (`30` §8). Defence in depth: the verifier-side R-CON-3 is load-bearing. | the publisher does not reference |

**What "down" means for non-orderable units** (D-0008 rule (6)): a value equal to one an intermediate registration superseded
(reversion), a unit removed, or a member set narrowed against its direction. Every other difference is a change the registration
authority selects; it is never computed as safe, and R-CON-5 lists it before security-relevant use on recorded machines.

## 4. Who selects content in CP-1 (computed)

Atoms: `rck` is the release-candidate key; `rfk1`, `rfk2` the release-final keys; `cust`/`regk` registration custodians and keys;
`vp`/`va` verification processes and keys; `repo` the repository writer delivering a release (rendered as `repo`, never as a
key; RV6-M1); `tsk` trust-state keys. Victims: `USE` is use of a Git-delivered release (C1–C2); `ING_P1` and `ING_P2` are
ingress with a P1 proof or in-gate state codes; `FA` is first admission.

<!-- CS7:BEGIN CP-CONTENT -->
Process compromise of a party implies its key; a set is not shown when the same set with a key in place of a process is also minimal (every minimal set: `minimal_sets_table`).

| Victim | Minimal sets: malicious non-orderable constitutional content effective (CP-1) |
|---|---|
| USE | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, 2 release-final keys, rck}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, repo}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, repo} |
| ING_P1 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, 2 release-final keys, rck} |
| ING_P2 | {insider}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, 2 release-final keys, rck}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, fcpub}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, src1, src2}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, src1, desig2}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, src1, op1src}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, src2, desig1}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, src2, op1src}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, desig1, desig2}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, desig1, op1src}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, desig2, op1src}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, fcpub}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, src1, src2}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, src1, desig2}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, src1, op1src}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, src2, desig1}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, src2, op1src}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, desig1, desig2}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, desig1, op1src}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, desig2, op1src} |
| FA | {insider}; {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {2 verification processes, pipeline}; {2 registration custodians, 2 verification keys, pipeline}; {2 registration custodians, 2 verification keys, 2 release-final keys, rck}; {2 registration keys, 2 verification keys, 2 trust-state keys, pipeline, fcpub}; {2 registration keys, 2 verification keys, 2 trust-state keys, 2 release-final keys, rck, fcpub} |
<!-- CS7:END CP-CONTENT -->

**Statements that follow from the computed sets** (checked by `decision-register/statements_check.py`):
- No set consists of release keys, pipeline, trust-state keys, transport or repository atoms only (INV-RF).
- Every set that is not a residual or a first-contact root set contains either the registration threshold (custodians or keys)
  with two verification compromises, or pipeline input with two verification processes: route TB-4′ (INV-CONTENT).
- The delegated 2-of-3 quorum, restricted by two verification records, is the selector of content (OP-2 (b)).

## 5. Forward compatibility (HO-0001 §4)

A new constitutional file shipped in a kernel (for example the Capability Acceptance Contract Markdown and compiled YAML, the
Gate W artifact-flow policy, or the G0–G6 health scheduler) is classified by inventory data (`23` §7.1). Its content is fixed per
release by R-CON-1 like every other non-join unit, and its effective value needs R-CON-3. Default deny holds for an unclassified
file. With the carried R-CON-5 requirement, its per-project listing also comes from inventory data (`security_classified`), not
from its path. RV5-I2 (derivation between members of an owner-domain binding group) is carried to the capability-contract phase
as RT-182.

## 6. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| TB-4 (route I) | an insider change accepted by honest verification | process; two independent records | — |
| TB-4′ (TA-11) | two compromised verification processes plus pipeline input | §4 sets | CS7 `G_CONTENT` |
| RA-1 | 2 of 3 registration custodians with two verification compromises | §4 sets; R-CON-5 lists non-reduction changes on recorded machines | CS7; CON6 |

## 7. Evidence

| Evidence | Kind | Result |
|---|---|---|
| `evidence/r6/CON6-first-hand-constitutional-content.{py,json}` (retained; the rules R-CON-1…R-CON-4 are unchanged in substance) | executed (pack checker; real legacy 4.1.5 as the consumer) | ceremony refuses the CI-derived proposal (exit 3); signs the first-hand proposal (0); E7 refuses the attacker kernel (3); genuine kernel eligible (0); changes listed (8); undeclared reversion refused (6); withheld intermediate registration `INCOMPLETE` (7); harm control on 4.1.5 |
| `evidence/r6/P4r6-conformance-oracle.{py,json}` section G | computed (retained) | E7 restrictor scenarios |
| `constitutional-surface/csi_check.py selftest` | executed | S71–S77 and the full self-test (`22` §1) |
| `evidence/r7/CS7-derivation-calculator.json` goal `G_CONTENT` | computed | INV-CONTENT and INV-RF hold for CP-1; `V_CANDIDATE_BINDING`, `V_E7_RESTRICTORS`, `V_VERIFICATION_COUNT` load-bearing |
| `evidence/r7/r6-probes/` B-A10 and D-A03 re-runs | executed | the RV6-L1 behaviour as carried (unflagged unlisted-path changes are not listed; listed with the flag) |
