# Output 29 — Fact derivation and selection authority (rule FD-1)

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> **Revision 6** closes blocking class **BC5-4** (review r5 CD5-4; RV5-M5, CR5-B-05, RV5-L5, D-A07):
> - the decision register is complete (§4) and is a data file of the pack (`decision-register/DECISION_REGISTER.yaml`), checked
>   by `decision-register/register_check.py`;
> - every selector substitution named there is a strategy of the revision-6 derivation calculator (`evidence/r6/CS6-*`);
> - every consequence statement is a generated calculator block, checked by `decision-register/statements_check.py` (§5.5).
>
> New in revision 5. It states, as one rule with mechanical checks, the property whose absence let the same rejection class
> survive: **a lower-trust input yielding a current, higher-trust fact** (D-0007). Normative keywords: MUST, MUST NOT, SHOULD.

## 1. Why a rule about facts

Every revision up to 4 applied D-0007 to **inputs**. Each statement was verified for its purpose and threshold, and each
constitutional file was classified. The facts that decisions consume were still derived from those inputs through three
shapes that no rule forbade:

| Shape | What happened | Findings |
|---|---|---|
| **Selection from an authorised set** | an authority approved a set; a lower-trust party chose which member became effective | RV4-H3, RV3-H2, R2-H2, RV4-M3, RV4-L10; **RV5-H1** (the first-contact value chose lineage, quorum and evaluator) |
| **Pass-through** | a higher-threshold signer signed a fact it did not establish | RV4-H1, RV3-H3, RV4-D-A07; **RV5-H3** (the registration signed a CI-derived unit map); **RV5-H2** (an image record nobody established) |
| **Evaluator inside the object** | the object whose trust was being decided evaluated, or supplied the bytes for, its own acceptance | RV4-H2, RV-H3 |

Revision 5 stated FD-1 but listed only the decisions it changed. Every false consequence statement review r5 found lay in a
decision the register omitted, and no test could detect those defects (D-A07). Revision 6 makes the register complete and
derives every statement from it.

## 2. The rule

**FD-1 (fact derivation and selection authority).** For every trust decision *D* that confers authority α(*D*) and currency
κ(*D*):

1. **Roles.** Every input of *D* has exactly one role in the decision register (§4):
   - a **selector**, whose value determines which of several authentic candidates becomes the effective fact;
   - a **restrictor**, which can only refuse, or strengthen through a monotone join;
   - a **carrier**, which transports bytes whose identity a selector already fixed.
2. **Selector authority.** Every selector MUST have authority ≥ α(*D*) and currency ≥ κ(*D*) (§3). Restrictors may come from
   any authenticated input. Carriers may come from anywhere.
3. **First-hand establishment.** A signature contributes to a selector's authority only for a fact its signer established
   itself.
4. **No self-evaluation.** The artefact under judgement is never a selector, and never the evaluator of its own acceptance.
5. **Shortfall.** A decision whose selector cannot be supplied at the required authority and currency fails closed, unless the
   pack states the shortfall as a residual with an exact bound, a label on every surface that shows the state, and an
   acceptance test that fails when the bound is exceeded. The register marks such a decision `shortfall` (DR-15, DR-25,
   DR-33). The first-contact root is the shortfall of DR-02…DR-06, stated in `32` §6.

**FD-2 (derived strength).** The strength of a fact is the minimum, over every input that can change or select it, of that
input's authority. Where a derivation can be enumerated, the minimum is **computed**, never argued (FD-3).

**FD-3 (computed minima).** Every statement of the pack of the form "an accepted malicious binary (or effective content)
needs at least …" MUST be the output of the derivation calculator (§5.3) for the stated owner answers, with pipeline and
infrastructure inputs as atoms. Hand-enumerated routes are not evidence (§5.5).

## 3. Authority and currency

**Authority** (highest first):

| Rank | Authority |
|---|---|
| 1 | the root threshold |
| 2 | a quorum of at least two distinct keys of one purpose whose keys hold no other purpose, each establishing the fact first-hand; or local machine authority: a human typing a value read now from independent sources, a protected operator pin within its validity, a local confirmation |
| 3 | one key of one purpose |
| 4 | the repository writer, project configuration, the governed account |
| 5 | transport, unauthenticated input, the pipeline, the artefact under judgement |

**Currency** (highest first): established now (typed in the gate or at first contact) > within a stated window (P1 pin or
confirmation naming that state; P3 witnesses) > as of a past anchor or compiled state > none.

Custody independence (different people, organisations, build environments, first-contact sources) is not verifier-checkable at
any rank. It is a stated assumption (TA-4, TA-5, TA-10′, TA-11) wherever a rank relies on it.

## 4. Decision register (complete; R-SEL-1)

**Scope.** The register lists every trust decision of RoT-1. Two checks keep it complete:
- **Rule completeness (C2).** `register_check.py` requires every rule id defined in the rule tables of `05`, `19`, `25`, `30`,
  `31`, `32`, `33` and `34` to belong to at least one decision.
- **Calculator coverage (C5).** Every CS6 rule is referenced by at least one row. A rule that the calculator's own mutation
  analysis reports as not load-bearing in its model is referenced together with an oracle or executed scenario that fails
  without it.

**Sources and checks.**
- The table below is rendered from `decision-register/DECISION_REGISTER.yaml` and must equal the rendering (C7).
- The binary compiles the same file (R-SEL-1; its digest is in the TBM, `25` §4).
- Restrictor tags name the calculator rule (`V_…`, `H_…`) and the scenarios that fail when the restrictor is removed:
  `P4r6:` oracle rows, `P4r5u:` P4r5 rows re-run under revision-6 rules, `FA6:`, `CON6:`, `ENV6:`, `ADM6:`, `UW6:`, `SRC6:`,
  `ATTR6:` executed probes, `DA03r6:` mutants, `CSI6:` checker cases and `LAY6:` legacy matrix properties.

Decisions revision 5 omitted, and review r5 required: first-contact lineage (DR-03), state (DR-04), source quorum (DR-05) and
evaluator (DR-06); first admission versus re-admission (DR-10); the build environment (DR-13); verification binding (DR-15);
registered-content derivation (DR-16); restrictor revocation (DR-19); release selection among eligible releases under OP-11 (a)
(DR-25, a stated shortfall, no longer labelled a carrier).

<!-- REGISTER:BEGIN -->
| ID | Decision (confers) | Selectors (authority; currency) | Restrictors | Carriers | Calculator (CS6) | Tests | Specified in |
|---|---|---|---|---|---|---|---|
| DR-01 | TCB acceptance of binary B, running mode (T0) | **source identity, input manifest, environments, content, final, targets**: the release registration, rank 1 (OP-2 (a)) or rank 2 (OP-2 (b)); referenced by the selected Trust State<br>**bytes**: first-hand reproduction quorum of at least two single-purpose reproducer keys (rank 2); reproductions of the registered release<br>**publication and negatives**: the selected Trust State (trust-state purpose within the anchored chain); inclusion anchor plus a currency proof naming that Trust State (P1 naming it, P2, P3) | AP-4 negatives (binary, release, registration, registered final and candidate) (`P4r6:R6-AP-R1_registered_final_revoked`, `P4r6:R6-AP-R2_registered_candidate_revoked`, `P4r6:R6-AP-R2b_registration_revoked` …)<br>AP-4 binary floor (min_binary_version) (`P4r6:R6-AP-R4_binary_below_min_binary_version`, `DA03r6:R6-min-binary-version`)<br>AP-5 verification count (`V_VERIFICATION_COUNT`; `DA03r6:R6-A4b-attestation-not-registered`)<br>AP-5 candidate and kernel binding (R-CON-2) (`V_CANDIDATE_BINDING`; `P4r6:R6-AP-R3_attestation_for_another_candidate_same_source`, `P4r6:R6-AP-kernel_attestation_for_other_kernel`, `P4r6:R6-AP-kernel_final_kernel_differs_from_registration` …)<br>AP-5 REJECTED attestation (`V_REJECTED`; `P4r6:R6-AP5r_trust_state_revocation_does_not_clear_REJECTED`, `DA03r6:R6-A4b-ignores-REJECTED`)<br>AP-5 registration referenced by the selected Trust State (`V_REGISTRATION_REFERENCED`; `DA03r6:R6-registration-not-referenced`)<br>AP-5 registered final restrictor (`DA03r6:R6-final-restrictor`, `DA03r6:R6-A8-omits-candidate`)<br>AP-6 quorum of distinct one-signature reproducer keys (`V_QUORUM`; `DA03r6:R6-single-signature`, `DA03r6:R6-count-statements`, `DA03r6:R6-revoked-reproduction-counted`)<br>AP-6 conflict (R-REP-5′) (`V_CONFLICT`; `DA03r6:R6-conflict`)<br>AP-6 OP-9 (d) registered digest (`V_OP9D_DIGEST`)<br>AP-7 publication (`V_PUBLISHED`; `DA03r6:R6-A5-publication-not-required`)<br>AP-8 TBM and accepted-TBM high-water (`DA03r6:R6-A7-disabled`, `DA03r6:R6-tbm-source`, `DA03r6:R6-first-run-record`)<br>AP-3 currency proof names the selected Trust State (`V_P1_NAMES_STATE`; `DA03r6:R6-descendant-proof`, `DA03r6:R6-A9-not-applied`)<br>targets registered (`DA03r6:R6-target`) | Git host, pipeline, mirrors, bundles, download host | `registration_routes` G_SRC/G_INPUTS<br>`build` G_BYTES<br>`thief_selectable` G_BYTES | RT-134, RT-129, RT-153, RT-165, RT-169 | 25 §5, 30 §5–§8 |
| DR-02 | TCB acceptance at first admission (bootstrap mode) (T0 on a machine with no prior trust) | **state, lineage, source quorum and evaluator (through DR-03…DR-06)**: the first-contact root of the owner's OP-13 answer (rank 2 local authority); codes read now from the OP-13 sources | AP-4…AP-8 as DR-01, in gov-admit (shared vectors R1–R5) (`FA6:R1_registered_final_revoked`, `FA6:R3_attestation_for_another_candidate_same_source`, `FA6:R5_attestation_for_registered_candidate_other_kernel` …)<br>candidate never executed; self-evaluation refused (`FA6:S1_FA5_scenarios_vectors_mutants_unchanged_on_r6`) | download host, bundles, Git host | `fc_state_root` G_BYTES/G_CONTENT | RT-135, RT-136, RT-169 | 31 §3–§4, 25 §5, 32 |
| DR-03 | First-contact lineage selection (the root chain on a machine with no prior trust) | **lineage_id of the first-contact manifest bound by the agreed code**: the first-contact root (rank 2 local authority); under OP-13 (c)/(d) also the compiled lineage of the registered admitter (rank 1 or 2); now | FC-6 lineage from the typed value, never bundle order (`V_FC_LINEAGE`; `FA6:ORD-1_attacker_root_first_genuine_code`, `FA6:lineage_from_bundle_order`)<br>FC-7 compiled lineage under OP-13 (c)/(d) (`V_FC_LINEAGE`; `FA6:FIRST_CONTACT_LINEAGE_NOT_COMPILED`, `FA6:skip_compiled_lineage`) | bundles, download host | `fc_lineage_sub` G_BYTES/G_CONTENT | RT-156, RT-158, RT-159 | 32 §5, 25 AP-2 |
| DR-04 | First-contact state selection (the selected Trust State (publication, negatives) at first admission) | **state_epoch of the first-contact manifest bound by the agreed code**: the first-contact root (rank 2 local authority); now (bounded by issued_at and valid_until) | FC-5 manifest bound by the code (`FA6:FC-5_manifest_not_the_one_the_code_names`, `FA6:skip_fcm_digest_check`)<br>FC-2 procedure manifest hash (`FA6:FC-2_procedure_manifest_hash_mismatch`) | bundles, download host | `fc_state_root` G_BYTES | RT-156 | 32 §3–§5, 25 AP-3 |
| DR-05 | First-contact source quorum (how many independent sources must agree at first admission) | **the owner's OP-13 answer compiled into the registered admitter**: the registration of the admitter release (rank 1 or 2); the admitter build | FC-4 compiled quorum; the Trust Policy may only raise it (`V_FC_COMPILED_QUORUM`; `FA6:quorum_from_selected_state`, `FA6:CHANNEL_QUORUM_NOT_MET`)<br>FC-1 procedure: every required source read, codes identical (`FA6:FC-1_procedure_pages_disagree`) | independent sources as carriers of the code | `srcs` G_BYTES | RT-156, RT-158 | 32 §4–§5 |
| DR-06 | Evaluator selection at first admission (which code evaluates the first TCB) | **admitters[target] of the manifest bound by the agreed code, compared with the platform hash tool; under OP-13 (c) the platform code signature**: the first-contact root (rank 2 local authority); the admitter digest is registered and reproduced (rank 1 or 2); now | FC-3 admitter digest in the agreed manifest (`V_FC_EVALUATOR`; `FA6:FC-3_procedure_admitter_digest_not_in_manifest`, `FA6:PLATFORM_SIGNATURE_INVALID`)<br>FC-8 evaluator binding (listed, not revoked, manifest consistent) (`FA6:ADMITTER_NOT_LISTED`, `FA6:ADMITTER_REVOKED`, `FA6:FIRST_CONTACT_MANIFEST_INCONSISTENT` …) | package manager, owner site, download host | `fc_eval_sub` G_BYTES/G_CONTENT | RT-157, RT-159 | 32 §4–§5, 31 R-ADM-2′ |
| DR-07 | Evaluator of later binaries (acceptance of binary N+1) | **the admitted gov N**: its own admission (DR-02 or DR-01); its admission record within validity | GB-3 own revocation (OP-15) (`FA6:S1_FA5_scenarios_vectors_mutants_unchanged_on_r6`) | — | outside: the evaluator is the TCB accepted by DR-01/DR-02; bounded by GB-1′…GB-3 | RT-137 | 31 §3, §5 |
| DR-08 | Bytes that run as gov (the enforced TCB bytes) | **the bytes the evaluator measured, installed from its buffer**: the evaluator of DR-02/DR-07; at installation | GB-4′ TCB-location predicate for C3 and ceremonies (`UW6:ceremonies_refused_on_user_writable_install`, `UW6:every_stated_row_equals_computed`)<br>GB-6 effective uid 0 writable (`FA6:CR5-B-12_euid_0_location_predicate`)<br>R-ADM-6 installation from the buffer (`ADM6:A08_fail_closed`) | file system | outside: same-account replacement is A3 (RS-3); GB-4′ and GB-6 bound C3 and ceremonies | RT-138, RT-139, RT-171 | 31 §4–§5, §7.1 |
| DR-09 | Admission record honoured (genuine-binary rule) and ceremony order (C1–C3 and TA-5 ceremonies for a running binary) | **an admission record in the protected verifier trust store naming the running digest**: gov-admit or the admitted gov (DR-02/DR-01); valid_until | GB-1′ records honoured only inside the store (`ADM6:A15_record_outside_store_not_honoured`, `FA6:RV5-B-A15_record_shipped_beside_binary`, `FA6:record_anywhere`)<br>GB-2 expiry (`FA6:S1_FA5_scenarios_vectors_mutants_unchanged_on_r6`) | file system | outside: A3 can forge records in its own account location (GB-5, RS-3) | RT-137, RT-171 | 31 §4–§6 |
| DR-10 | First admission versus re-admission (whether a pre-existing verifier trust store is moved aside) | **whether the store for the lineage holds an admission record**: the local verifier trust store written by gov-admit (rank 2 local authority); at admission | R-ADM-8′ move-aside only at first admission (`ADM6:A09_readmission_keeps_store`, `ADM6:A09b_first_admission_moves_recordless_store`, `FA6:move_aside_every_run`)<br>R-ADM-13 exclusive lock (`ADM6:A11_lock_no_record_moved_aside_one_store`) | file system | outside: monotonic-state availability; bounded by AD-2 and R-ADM-13 | RT-139, RT-170, RT-181 | 31 R-ADM-8′, R-ADM-13 |
| DR-11 | Source identity of release R (F-SRC) | **source {release_commit, git_tree, content_digest v2}**: the release registration (rank 1 or 2), each custodian recomputing from its own fetch; at registration | R-REG-3 (d) first-hand verification records for exactly the candidate (`H_REG_RECORDS_FIRST_HAND`; `P4r6:R6-CER-records_for_another_candidate`, `P4r6:R6-CER-records_not_first_hand`, `DA03r6:R6-ceremony-first-hand-records`)<br>source identity v2 refusals (`SRC6:T1_v2_refuses_carrier_path`, `SRC6:T1_v2_encoding_alone_distinguishes`)<br>R-VER-3 verification selects nothing alone (`V_VERIFICATION_COUNT`) | Git host, pipeline | `registration_routes` G_SRC | RT-130, RT-172 | 30 §4.1, §5, §6 |
| DR-12 | Build inputs (toolchain archives, lockfile) (F-INPUTS) | **input manifest v2 (toolchain, lockfile)**: the release registration after upstream checksum checks (rank 1 or 2); at registration | R-REG-3 (a), (b) upstream checks by custodians (`H_REG_UPSTREAM`; `ENV6:E2_code_ENVIRONMENT_COMPONENT_UNVERIFIED`)<br>R-VER-1 upstream checks by verifiers (`H_VER_UPSTREAM`; `ENV6:E2_code_ENVIRONMENT_COMPONENT_UNVERIFIED`)<br>R-REP-2 inputs by digest (`H_REP_BY_DIGEST`; `ENV6:E3_code_INPUT_DIGEST_MISMATCH`)<br>R-REP-9 OP-10 (b)/(c) (`H_REP_BY_DIGEST`) | mirrors, caches, CI configuration | `registration_routes` G_INPUTS/G_TOOLCHAIN | RT-130, RT-131, RT-133 | 30 §4.2, R-REG-3 |
| DR-13 | Build environment identity (F-ENV) | **environment manifests (components, recipe, tree digest, supplier class)**: the release registration, established by at least two first-hand environment reproductions (rank 2 quorum under the rank 1 or 2 registration); at registration | R-BENV-2 environment reproduction quorum (no pipeline record) (`H_REG_ENV_QUORUM`; `ENV6:E1_code_ENVIRONMENT_NOT_REPRODUCED`, `ENV6:E8a_code_ENV_REPRODUCTION_CONFLICT`)<br>R-BENV-1 components pinned upstream (`H_REG_UPSTREAM`; `ENV6:E2_code_ENVIRONMENT_COMPONENT_UNVERIFIED`)<br>R-BENV-4 reproducers re-assemble (`H_REP_ENV_REASSEMBLE`; `ENV6:E3_code_INPUT_DIGEST_MISMATCH`)<br>R-BENV-5 diversity under OP-16 (b) (`V_ENV_DIVERSITY`; `ENV6:E9_code_ENVIRONMENT_DIVERSITY_NOT_MET`, `ENV6:E5_code_REPRODUCTION_CONFLICT`) | image registries, mirrors, caches | `build` G_ENV | RT-160, RT-161, RT-162 | 33 |
| DR-14 | Faithful build of a registered release (bytes) (F-BYTES) | **reproductions of the registered source, inputs and environment**: at least max(2, OP-9 quorum) distinct single-purpose reproducer keys, first-hand (rank 2); reproductions of the registered release | R-REP-3 first-hand confirmation to the publisher (`H_REP_FIRST_HAND`)<br>R-REG-3 (f) custodians' own reproduction under OP-9 (d) (`H_REG_OWN_REPRODUCTION`)<br>R-REP-5′ conflict refuses (`V_CONFLICT`; `P4r6:R6-AP5r_trust_state_revocation_does_not_clear_conflict`)<br>05 §7 rule 2 candidate and final signers sign only what they rebuilt (`H_SIGN_REPRODUCE`; `P4r5u:VA5-06_RV3-D-A03_final_promoted_from_genuine_candidate`, `P4r5u:VA5-05_RV3-D-A03_op4_no_everyday_key`; defence in depth of V_QUORUM (DR-01)) | pipeline, download host | `build` G_BYTES | RT-133, RT-134, RT-153 | 30 §7 |
| DR-15 | Verification records counted (binding) (the OP-8 verification restrictor of source, content and bytes) | **shortfall (FD-1 §2 (5))**: verification records select nothing; they restrict (TB-4′ when OP-8 verification processes are compromised); residual TB-4′ | R-VER-1 the verifier attests exactly the candidate and kernel it reproduced (`H_VER_BINDS_CANDIDATE`; `P4r6:R6-AP-kernel_attestation_for_other_kernel`, `CON6:B_ceremony_refuses_CI_derived_registration`)<br>R-VER-2 / R-CON-2 counted attestations bound to the registered candidate and kernel (`V_CANDIDATE_BINDING`; `P4r6:R6-AP-R3_attestation_for_another_candidate_same_source`, `FA6:R5_attestation_for_registered_candidate_other_kernel`) | owner ceremony channel | — | RT-165 | 30 §6, 34 R-CON-2 |
| DR-16 | Registered constitutional content (kernel tree, non-join units, migrations) (F-CON) | **the constitution and migrations blocks of the registration**: the release registration, each custodian deriving them first-hand from its own kernel build (rank 1 or 2); at registration | R-CON-1 first-hand derivation (`H_REG_CONTENT_FIRST_HAND`; `P4r6:R6-CER-D-A01_ceremony_derives_content_first_hand`, `CSI6:S72`, `CON6:B_ceremony_refuses_CI_derived_registration` …)<br>R-REG-7 V8 producer restrictor (final and candidate kernel and source equal) (`P4r6:R6-E7-D-A01_variant_registration_names_attested_candidate`) | pipeline, kernel payload, Git delivery | `content_accepted` G_CONTENT | RT-163 | 34 §3, 30 R-REG-3 (g), R-REG-6, 23 §12 |
| DR-17 | Registration effective on a machine (that release R's registration is known and in force) | **the effective or selected Trust State referencing the registration**: trust-state purpose within the anchored chain (currency per DR-20), or the first-contact root; as DR-20 | R-PUB-1′ publisher applies E7's restrictors (`H_PUB_REGISTRATION_RESTRICTORS`; `P4r6:R6-E7-D-A01_attacker_candidate_and_final_weak_kernel`; defence in depth of V_E7_RESTRICTORS (DR-23))<br>R-REG-5 first-hand delivery to the publisher (`H_REP_FIRST_HAND`)<br>registration referenced (`V_REGISTRATION_REFERENCED`; `DA03r6:R6-E7-referenced`) | Git host, bundles, transport | `published_by_owner` G_CONTENT/G_BYTES | RT-164 | 30 §8 |
| DR-18 | Binary publication and negatives (F-PUB) | **published_binaries[] and revocations of the selected Trust State**: trust-state purpose within the anchored chain; as DR-20 | AP-7 publication (`V_PUBLISHED`; `DA03r6:R6-A5-publication-not-required`)<br>R-PUB-3 one digest per release and target (`V_CONFLICT`) | transport, bundles | `published_by_owner` G_BYTES | RT-134 | 30 §8, 25 AP-7 |
| DR-19 | Restrictor revocation (removal of a REPRODUCTION_CONFLICT or ARTIFACT_SOURCE_REJECTED refusal) | **a registration-revocation statement naming the restricting statement**: the registration authority at threshold (rank 1 or 2); held | AP-5r a trust-state or revocation-key revocation removes no restrictor (`V_REVOCATION_AUTHORITY`; `P4r6:R6-AP5r_trust_state_revocation_does_not_clear_conflict`, `P4r6:R6-AP5r_trust_state_revocation_does_not_clear_REJECTED`, `FA6:trust_state_revokes_restrictors` …) | Git host, bundles | `build` G_BYTES | RT-168 | 30 R-REG-11, R-REP-5′, 25 AP-5r |
| DR-20 | Current trust state for C3 and binary acceptance (currency) | **inclusion anchor plus a currency proof naming the effective Trust State (P1 naming it, P2 in-gate fingerprint, P3 witnesses)**: rank 2 local authority, or witness keys at the C3 threshold under two custodians; now (P2) or within the window (P1, P3) | 24 §4.4 P1 proof covers only the Trust State it names (CR4-B-07 option 1) (`V_P1_NAMES_STATE`; `DA03r6:R6-descendant-proof`)<br>24 §8 clock high-water and future statements (CR5-B-08) (`P4r6:R6-CLOCK-CR5-B-08_restored_store_clock_back_newer_statements_delivered`, `DA03r6:R6-clock-future`, `DA03r6:R6-clock-high-water`)<br>21 OP-3 mode B needs a proof naming the publishing Trust State (RV5-L9) (`P4r6:R6-OP3-B-RV5-L9_mode_B_update_without_proof_naming_publishing_TSS`, `DA03r6:R6-mode-B-currency`) | repository, bundles, transport | `thief_selectable` G_BYTES/G_CONTENT | RT-101, RT-147, RT-148, RT-178, RT-179 | 24 §3.4, §4.4, §8 |
| DR-21 | Anchoring events (pins, confirmations, in-gate proofs) (anchors) | **a protected pin, a human confirmation on a protected installation, an in-gate fingerprint**: rank 2 local authority; pin validity; confirmation window; now for in-gate | 24 §3.5 pin integrity predicate; GB-4′ anchoring ceremonies need a protected installation (`UW6:every_stated_row_equals_computed`) | file system | `thief_selectable` G_BYTES | RT-102, RT-103, RT-138 | 24 §3.2, §3.5, 31 GB-4′ |
| DR-22 | Witnessed state (OP-7 (c)) (currency on witness-reliant machines) | **freshness witnesses naming the effective Trust State**: at least two witness keys under two custodians, input from the ceremony or the channel; witness validity | KS-11 witness keys single-purpose, C3 threshold 2 (`P4r5u:AP-00b_stateless_witnessed_runner_op7c`) | Git host, bundles | `thief_selectable` G_BYTES | RT-104, RT-149, RT-154 | 24 §3.3, 05 §3 |
| DR-23 | Policy-root eligibility of release R (E1–E10; T1-E) (the release whose kernel is the policy root) | **the registration of R referenced by the effective Trust State**: the registration authority (rank 1 or 2) with OP-8 verification bound to the registered candidate and kernel; as DR-17 and DR-20 (ingress) | R-CON-3 E7 applies AP-5's restrictors (`V_E7_RESTRICTORS`; `P4r6:R6-E7-D-A01_attacker_candidate_and_final_weak_kernel`, `P4r6:R6-E7-D-A01_op4_no_one_everyday_key`, `P4r6:R6-E7-B-A06_registration_without_verification_record` …)<br>R-CON-4 reductions computed at the verifier (INCOMPLETE when a referenced registration is not held) (`CSI6:S73`, `CSI6:S74`, `CON6:B_A10_reversion_refused_at_verifier_and_withheld_intermediate_incomplete`)<br>23 §12.3 exact per-release lookup (units and final equal the registration) (`DA03r6:R6-E7-units`, `CSI6:S58`)<br>floors joined, registered precedence, E3/E4/E9/E10 (`CSI6:S26`, `CSI6:S31`) | kernel payload, Git delivery | `content_accepted` G_CONTENT | RT-164, RT-166, RT-140 | 19 §6, 34 R-CON-3, R-CON-4, 23 §12.3 |
| DR-24 | Effective non-orderable value of a unit (the value a consumer enforces) | **the registration of the policy-root release; else that of the running binary's embedded release; else SURFACE_VALUE_UNAVAILABLE**: as DR-23; as DR-23 | consumer register fail-closed meaning (`CSI6:S35`) | kernel bytes | outside: derived from DR-23; fail-closed meaning per the consumer register (23 §6.3) | RT-140, RT-107 | 23 §6.3, §12.3, 19 §5.2 |
| DR-25 | Release selection among eligible releases (OP-11 (a)) (which eligible registered release a project uses on a machine without a per-project record) | **shortfall (FD-1 §2 (5))**: the repository writer (rank 4) delivers which eligible registered release is installed on a machine with no per-project record; every candidate is a genuine eligible release with its own registered content; residual RR-2 | E10 per-project record refuses a downgrade without a transaction (`P4r5u:E7-D-A06_git_delivered_forged_final_unregistered`)<br>OP-11 (b)/(c) min_release_sequence and eligible_until (`CSI6:S57`) | Git delivery | — | RT-31, RT-118 | 21 OP-11, 20 RR-2, 19 E9, E10 |
| DR-26 | Registration changes on recorded projects (security-relevant use of a release whose non-orderable units changed) | **the new registration's unit values**: the registration authority (rank 1 or 2); as DR-17 | R-CON-5 security-classified changes listed in the per-project gate (`CSI6:S75`, `CSI6:S76`, `CON6:B_A09_variant_and_tool_command_listed_for_gate`)<br>R-REG-8 lowering history for computed reductions (`CSI6:S63`, `CSI6:S64`, `CSI6:S70`) | Git delivery | `content_accepted` G_CONTENT | RT-141, RT-166, RT-167 | 34 R-CON-5, 23 §12.4 |
| DR-27 | Owner constitutional file set (owner-domain constitutional content) | **a local confirmation or protected decision pin naming the binding-group digest**: rank 2 local authority; confirmation or pin validity | exact set match of the binding group (`CSI6:S66`, `CSI6:S67`) | repository | outside: local authority; RV5-I2 derivation carried as RT-182 | RT-120, RT-143, RT-182 | 23 §7.2 |
| DR-28 | Installation state COMPLETE (that the working tree is a RoT-1 installation) | **the closed entry sets recorded by the install transaction (trust top level including .gitattributes, kernel content set, statement directories, occupation)**: the install transaction of an admitted binary; at use | 18 §9.1 closed entry sets and nested markers (`LAY6:R2-H4_violations`, `LAY6:LP-1s_restated_rev6`, `ATTR6:member_protects_under_RV5-C-M1_configurations`) | working tree, Git | outside: legacy containment property R2-H4 (LAY6 matrix: 0 violations) | RT-50, RT-144, RT-173, RT-174, RT-176 | 18 §9.1, 26 |
| DR-29 | Project root for a command (which installation a command acts on) | **the nearest ancestor holding governance/trust/FORMAT**: the working tree (restricted by refusal inside the Protected Path Set and the transaction area); at use | 18 §9.2 refusal inside the PPS and the transaction area (`LAY6:LP-1r`) | working directory | outside: legacy containment (LAY6) | RT-144, RT-175 | 18 §9.2 |
| DR-30 | Migration content (overlay migrations applied by the install transaction) | **migrations registered with the release**: as DR-16 (first-hand derivation); as DR-23 | Overlay Surface whitelist; strength vector; CR4-B-04 (`CSI6:S46`, `CSI6:S47`, `CSI6:S48`) | release payload | `content_accepted` G_CONTENT | RT-109, RT-146, RT-163 | 23 §11–§12, 19 §9 |
| DR-31 | Root version validity (key grants and thresholds) | **root version N+1**: thresholds of root N and N+1 (rank 1); held | Fact Threshold Check KS-9′, KS-10′, KS-12, KS-13, KS-14 (`P4r6:R6-KS14_root_threshold_1`, `FA6:KS-14_root_v1_threshold_1`, `FA6:skip_min_root_threshold` …) | bundles, Git host | outside: root threshold compromise is A8 (outside TA-4) | RT-132, RT-177 | 05 §3 |
| DR-32 | Trust Policy acceptance (floors, classification, bootstrap and registration parameters) | **Trust Policy version**: the root threshold (trust-policy purpose); held, monotone | 19 §10.6 computed reductions (`CSI6:S53`, `CSI6:S54`) | bundles, Git host | outside: root threshold (A8); computed reductions with cumulative lowering history | RT-78, RT-108 | 19 §10.6, 17 S3 |
| DR-33 | Clock-based proof usability (whether pins, the C3 window and witnesses count) | **shortfall (FD-1 §2 (5))**: the local clock (TA-7) with the stateful high-water; a restored store with the clock set back and every newer statement withheld cannot be distinguished; residual RS-2b | clock high-water raised by every ingested non-future statement; future statements disable clock proofs (`P4r6:R6-CLOCK-CR5-B-08_restored_store_clock_back_newer_statements_delivered`, `DA03r6:R6-clock-high-water`, `DA03r6:R6-clock-future`) | local clock | — | RT-56, RT-148, RT-178 | 24 §8, §10 |
| DR-34 | Trust-gate authorisation (trust transitions (update, downgrade, lowering, weakening, registration change)) | **a local confirmation or a protected decision pin**: rank 2 local authority; pin maximum validity; confirmation now | 27 §3.2 decision-pin maximum validity; confinement (`DA03r6:R6-decision-pin-max-validity`) | repository gate records (never authorising) | outside: local authority; A3 same account is RS-3/TG-2 | RT-89, RT-91, RT-103, RT-152 | 27 |
| DR-35 | Accepted-TBM high-water (refusal of older binaries) | **the TBM of a resolving release build at first run or verify-artifact acceptance**: the admitted binary's verifier trust store; monotone | CR4-B-08 first-run record only for resolving release builds (`DA03r6:R6-first-run-record`, `DA03r6:R6-A7-disabled`) | file system | outside: stateless runners lack it (TB-L4) | RT-93, RT-116, RT-151 | 25 §5, 24 §8 |
<!-- REGISTER:END -->

## 5. Mechanical checks

### 5.1 In the binary (R-SEL-1 … R-SEL-4)

| ID | Rule | Test |
|---|---|---|
| R-SEL-1 | The binary compiles the decision register of §4 (`DECISION_REGISTER.yaml`): for every decision, its selectors with their authority and currency, its restrictors and carriers. | RT-128 (register present and equal to the file; `register_check.py` passes) |
| R-SEL-2 | A decision reads a selector only through a type constructible from the registered source (`Selected<T>`). | RT-128 (compile-fail tests for an unregistered source) |
| R-SEL-3 | A new decision, or a new input of an existing decision, fails the build until it is registered. | RT-128 |
| R-SEL-4 | For each registered restrictor, the conformance suite has a mutant that removes it and a distinguishing scenario that fails; for each selector, a mutant that substitutes the next-lower-authority input. | RT-129; `evidence/r6/DA03r6-*`; FA6 S7; CS6 mutation analysis |

### 5.2 On every root version: the Fact Threshold Check (FTC; `05` §3)

SV-4 refuses a root version whose grants give a fact-establishing purpose less than its compiled minimum, or let its keys
hold another purpose. The checks are KS-9′, KS-10′, KS-12, KS-13 and, in revision 6, KS-14 (root threshold ≥ 2). A later
version gives `ROOT_VERSION_INVALID`; a root v1 gives `ROOT_CHAIN_INVALID`. Owner options raise these minima, never lower
them.

### 5.3 Before a root ceremony: the derivation calculator (FD-3)

`gov trust draft-policy --derivation` enumerates the owner's release-process model with honest parties acting only on
first-hand checks. It computes the minimal capability sets for each attack goal and victim class, and fails the draft when an
invariant fails. The reference is `evidence/r6/CS6-derivation-calculator.py`:
- **Method.** Exact minimal true sets through minimal transversals, with no size bound, and monotonicity spot checks.
- **Atoms.** Processes, keys, infrastructure, first-contact capabilities and residual assumptions.
- **Goals.** Malicious source, inputs, bytes, mirror, toolchain, **environment** and **constitutional content**.
- **Victim classes.** P1, P2 (one and two sources), **witness-reliant runners (WR)**, **CI-record runners (CIR)**, **first
  admission under each OP-13 answer (FA)**, and content use and ingress (RV5-L5, CR5-B-10).
- **Strategies.** Every selector substitution of §4.
- **Rules.** One switch per restrictor.
- **Profile R5.** It turns off exactly the revision-6 rules, and must reproduce review r5's minima.

**Reference result (revision-6 rules; `22` §1).**
- 1,648 configurations; 38/38 self-checks.
- 4,840 invariant checks with 0 failures (INV-FC, INV-BYTES, INV-SRC, INV-ENV, INV-ENV-B, INV-ENV-PIPELINE, INV-CONTENT,
  INV-RF, INV-MIRROR, INV-ONE); 104,340 monotonicity checks with 0 violations.
- 91 revision-5 profile controls.
- Mutation analysis of all 27 rules. The 9 rules that are not load-bearing in the model are defence in depth; each is covered
  by an oracle or executed scenario (register C5).

### 5.4 Conformance oracle and mutation sensitivity

- `evidence/r6/P4r6-conformance-oracle.py` contains no expected-`ACCEPTED` attack row. Accepted attack sets live only in the
  calculator.
- `evidence/r6/DA03r6-oracle-regression-sensitivity.py` re-runs review r4's twenty single-rule mutants, the revision-5 rule
  mutants and the revision-6 rule mutants.
- `evidence/r6/FA6-first-admission.py` S7 mutates every revision-6 bootstrap rule.

### 5.5 Statements derived, register complete (revision 6; CD5-4)

| Check | Instrument | Fails when |
|---|---|---|
| Generated statements | `decision-register/statements_check.py` S1 | a `<!-- CS6:BEGIN key -->` block of any pack file differs from the calculator's statement, or a statement is placed nowhere |
| No hand-written minima | `statements_check.py` S2 | a brace set of calculator atoms outside a block is not a computed minimal set (revision-6 rules; revision-5 profile only on lines that name revision 5 or review r5) |
| Register completeness | `decision-register/register_check.py` C1–C8 | a rule id of the scoped files belongs to no decision; a selector has no calculator strategy or bound; a restrictor has no failing scenario; a CS6 rule is unreferenced; an RT does not exist; the table differs from the YAML; a referenced probe has a false verdict |
| Plan detection | `evidence/r6/DA07r6-plan-regression-detection.py` (RV5-D-A07 re-run) | a defect found by review r5 has no failing RT in `12` |

## 6. What FD-1 removes in each persistent class

| Class | Selector below authority | Revision-6 selector | Specified in |
|---|---|---|---|
| BC4-1 | one `build-attestation` key plus pipeline; one `verification-attestation` key; the release process | registration at rank 1 or 2; ≥ 2 first-hand reproductions | `30` |
| BC4-2 | transport and the candidate | first-contact root selects state; `gov-admit` evaluates; measured bytes installed | `31` |
| BC4-3 | threshold-1 `release-final` choosing among registered digests | the registration of exactly that release | `23` §12 |
| **BC5-1** | one channel page choosing lineage, quorum and evaluator | the agreed first-contact code over the OP-13 sources (the stated first-contact root); compiled quorum; lineage from the typed value; evaluator binding | `32` |
| **BC5-2** | an image record with no authority | environments established by first-hand reproduction from upstream-checked components; OP-16 residual | `33` |
| **BC5-3** | CI deriving the unit map; attestations reused across candidates; E7 without restrictors | first-hand derivation by custodians; attestations bound to the registered candidate and kernel; E7 with AP-5's restrictors | `34` |
| **BC5-4** | hand-written consequences over a partial register | the complete register; calculator strategies; generated statements | this file; `21` |

## 7. Residuals admitted under FD-1 §2 (5)

Each residual is stated, with its bound, label and test, where it is defined:
- RS-1, RS-1b, RS-1c, RS-2, RS-2b, RS-3…RS-5: `24` §10;
- AD-1′ (the first-contact root, FC-R1…FC-R4), AD-2, TB-1′, VR-B1′: `31` §9, `32` §10;
- TB-4, TB-4′, TB-S1, TB-S2, TB-S2′, TB-S3, AV-S1: `30` §12, `33` §8;
- RA-1: `34` §6;
- CS-1: `23` §10;
- RR-2 (DR-25): `20`;
- the VR-, LR- and TG- residuals: `18`, `26`, `27`.
