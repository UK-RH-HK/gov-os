# Output 28 — Why the classes survived six revisions, and what revision 7 changes in kind

> **RoT-1 revision 7 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Updated in revision 7 (AR-0019). §1–§10 are the analysis of revisions 5 and 6 (AR-0011, AR-0015), kept as the review trail;
> their option-specific rows are history (the option tree is not part of the certified profile CP-1, `35`). §11–§14 are new:
> the root cause of review r6's classes, what revision 7 changes in kind for CP-1, what remains a lower-trust input, the
> non-production control that shows what the revision-7 rules remove, and the attacks this architect ran against revision 7
> before hand-off.

## 1. The recurring class

Every rejection since 4.1.3 is one class: **a lower-trust input yielding a current, higher-trust fact.** Review r4 found it
three more times, each a narrowed remainder of a revision-2 class:

| Class | Lower-trust input (review r4 §9) | Higher-trust fact obtained | Parent |
|---|---|---|---|
| BC4-1 | one threshold-1 attestation key plus release-pipeline input | an accepted production binary | R2-H3 / BC-3 |
| BC4-2 | a transport- or source-host-selected revoked, remediated or self-reporting binary | the first trusted binary on a machine | R2-H2 / BC-2 ∩ R2-H3 / BC-3 |
| BC4-3 | a threshold-1 final choosing among registered non-orderable digests | the effective constitutional content of the newest release | R2-H1 / BC-1 |
| BC4-4 | — (statements derived from BC4-1…3) | owner-option and blast-radius consequences | BC-4 |

Review r5 found it again (§7), and review r6 again (§11).

## 2. Why each correction left a remainder (revisions 1–6)

| Revision | What it added | What a lower-trust party still selected |
|---|---|---|
| 1 | authenticated statements; release floors for selected keys | which authentic statements were seen; which keys counted; the binary (one `release-final`) |
| 2 | floors for 145 keys; monotonic state; `release-artifact` ≥ 2 | every unregistered leaf; a stateless machine's state; the commit every artefact signer checked |
| 3 | whole-payload classification; anchors; attested-source custodial stages | kernel precedence inside a join; the sequence number satisfying an anchor; the commit named by `release-final` |
| 4 | registration-only precedence; inclusion anchors and currency proofs; source from an ACCEPTED attestation | which registered digest (BC4-3); which binary is first and who evaluates it (BC4-2); who establishes the build and source facts (BC4-1) |
| 5 | rule FD-1; registration; reproduction quorum; `gov-admit`; release-scoped registration | which lineage, quorum and evaluator at first contact (BC5-1); which build environment (BC5-2); which constitutional content the registration signs (BC5-3); the statements derived from an incomplete register (BC5-4) |
| 6 | first-contact code over a manifest; environment reproductions; first-hand content; complete register over rule ids | **who composes, designates and submits** first-contact values (BC6-1); **how old** a first-contact value may be (BC6-2); **who authors** the environment manifest (BC6-3); **inputs outside the rule ids** (BC6-4) |

## 3. Root cause accepted in revision 5

No rule classified, per trust decision, which inputs may **select** the effective fact and at what authority and currency, and
no mechanism computed the resulting minimum. Rule FD-1 (`29`) is that rule; the decision register, the Fact Threshold Check and
the derivation calculator are the mechanisms.

## 4. What revision 5 changed in kind (history)

| Class | Revision-4 selector below authority | Revision-5 selector | Evidence |
|---|---|---|---|
| BC4-1 | `build-attestation` key + pipeline; one `verification-attestation` key; the release process | release registration; ≥ 2 first-person reproductions confirmed first-hand; withdrawn pass-through purposes | CS5; P4r5; DA03r5 |
| BC4-2 | tooling A2–A6; candidate-printed values; self-verification; ceremonies on the unaccepted binary | typed fingerprint; `gov-admit` over measured bytes; GB rules; ceremonies after admission | FA5; P4r5 |
| BC4-3 | threshold-1 `release-final` choosing among permitted digests | the registration of exactly that release | REG5; selftest 71/71 |
| BC4-4 | hand-derived tables | calculator output | CS5 |

## 5. What remained a lower-trust input in revision 5 (history)

Superseded by §9 and then §13. Two of revision 5's rows were wrong: "a human typing a fingerprint" was bounded only if that
fingerprint selected state alone (RV5-H1), and "reproducer environments" were bounded only if each reproducer's environment was
independently established (RV5-H2).

## 6. Attacks the architect ran against revision 5 before hand-off (history)

The revision-5 attack table (A-R5-01…A-R5-13) is kept at `4106885`. **What those attacks missed:** every attack substituted an
input the architect had already modelled; none substituted a selector the register did not list.

## 7. Root cause of review r5's classes (accepted in revision 6; history)

| Class | Mistaken equivalence | Lower-trust input | Higher-trust fact obtained |
|---|---|---|---|
| BC5-1 | *the typed fingerprint is a good selector of state, therefore of everything it commits to* | one channel page (rank 2), no key | the root of trust, the evaluator and the first TCB |
| BC5-2 | *every input named by digest ⇒ every input legitimately selected* | an image record with no assigned authority | the bytes of every production binary |
| BC5-3 | *the registration authority signed the unit map ⇒ the registration authority established it* | pipeline plus threshold-1 candidate and final keys | the effective constitutional content |
| BC5-4 | *a partial register plus a calculator over it ⇒ derived statements* | the architect's choice of which decisions to list | the owner's view of every consequence |

## 8. What revision 6 changed in kind (history)

Revision 6 bound first-contact values into one code over a manifest, established environments by reproduction, derived content
first-hand and made the register complete over rule ids. Its per-option rows are history at `4106885`.

## 9. What remained a lower-trust input in revision 6 (history)

Revision 6's table is superseded by §13. Its first row ("the first-contact sources of the OP-13 answer") was incomplete: the
manifest's composer, the designation of the sources and a package submitter also selected (RV6-H1), and stored values had no
age bound (RV6-H2). Its row "upstream environment suppliers" was incomplete: the manifest's author selected (RV6-H3).

## 10. Attacks the architect ran against revision 6 before hand-off (history)

The revision-6 attack table (A-R6-01…A-R6-15) is kept at `4106885`. **What those attacks missed:** every first-contact attack
substituted a source value; none substituted the party that composed, designated or submitted it, and none replayed an old but
genuine value. Every environment attack substituted a component; none substituted the manifest content itself.

## 11. Root cause of review r6's classes (accepted in revision 7)

| Class | Mistaken equivalence | Lower-trust input | Higher-trust fact obtained |
|---|---|---|---|
| BC6-1 | *a value agreed across independent sources is established by those sources* | the trust-state publisher (rank 3) composing the manifest; a carrier or unadmitted binary designating sources and steps (rank 5); a package submitter (rank 5) | the lineage, the evaluator and the first TCB |
| BC6-2 | *the value the operator uses at first contact is current* | a replayed, stored or designated value; a re-admission that ignores the store | a revoked, even malicious, binary as the current TCB |
| BC6-3 | *reproduced from the manifest by independent parties ⇒ the manifest was legitimately selected* | the author of the environment manifest; a supplier label | the bytes of every production binary |
| BC6-4 | *complete over the rule tables ⇒ complete over the inputs* | the scope of the architect's rule tables | the owner's view of consequences; what the plan can detect |

**The common cause.** Revision 6 checked completeness over the objects it had written (rule ids, decisions), not over the
values that enter decisions and the parties that establish them. A party that composes, designates, submits or authors a value
was invisible because no rule id named it. The option tree multiplied the combinations in which such a party mattered.

## 12. What revision 7 changes in kind (CP-1)

| Class | Revision-6 selector below authority | Revision-7 selector (CP-1) | Evidence |
|---|---|---|---|
| BC6-1 | the manifest composer; the designation; the submitter | the First-Contact Authority record at root threshold after the admitter's evidence; codes published only after each source custodian's first-hand verification; designation from the ceremony record at onboarding; no submitter or platform path (excluded) | FA7 S2 P, S2 D, S2 X, S3; CS7 INV7-NO-COMPOSER, INV7-NO-CARRIER |
| BC6-2 | stored and designated values without age; re-admission without store | compiled 24-hour state age on every path; AP-R1…AP-R6; R-CLK-1; residual CUR-R1 stated exactly | CUR7; ADM7 CLK; CS7 INV7-AGE, INV7-STORE |
| BC6-3 | the manifest author; labels; manifest-named keys | lock in registered source; derived manifests; authority with agreeing reproductions and the registration; provenance registries at root threshold; two toolchain lineages | ENV7 (real toolchain); CS7 INV7-ENV, INV7-ENV-PIPELINE, INV7-ENV-B, INV7-TC |
| BC6-4 | completeness over rule ids; text-level statement checks | completeness over every schema field and procedure input with its establishing party; atom-level statement checks with an injective renderer; independent detection | `register_check.py` C9–C11; `statements_check.py` S1a, S3; DA09r7; DA04r7 |
| (all) | an option tree of trust modes | one profile; every unselected mode absent or refused | PROF7 |

**Non-production control.** Switching off exactly the revision-7 rules reproduces the shapes review r6 found (the publication
process and a carrier each select the first TCB alone; stored codes admit a revoked binary even over a store that holds the
revocation; the pipeline selects the environment). These sets are what the rules remove; they are not options:

<!-- CS7:BEGIN CP-R6-CONTROLS -->
Non-production control: the revision-7 rules `H_FCA_ROOT_THRESHOLD`, `H_SOURCE_FIRST_HAND`, `V_TS_THRESHOLD`, `V_DESIGNATION_OUT_OF_BAND`, `V_FC_MAX_AGE`, `V_READMISSION_STORE`, `H_ENV_LOCK_IN_SOURCE`, `V_SUPPLIER_PINNED_KEYS`, `V_SUPPLIER_PROVENANCE`, `V_FINAL_THRESHOLD_2` switched off (the revision-6 shapes review r6 found). These sets are what the CP-1 rules remove; they are not options.

| Victim | Goal | Minimal sets with the revision-7 rules off |
|---|---|---|
| FA | malicious first TCB | {fcpub}; {carrier}; {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src}; {2 registration custodians, 3 reproducer processes} |
| FA | revoked binary at first admission | {fcpub}; {carrier}; {stored_old}; {win}; {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src} |
| RA_held | revoked binary at re-admission over a store holding the revocation | {fcpub}; {carrier}; {stored_old}; {win}; {src1, src2}; {src1, desig2}; {src1, op1src}; {src2, desig1}; {src2, op1src}; {desig1, desig2}; {desig1, op1src}; {desig2, op1src} |
| P1 | malicious build environment | {pipeline}; {env_up_a}; {env_common}; {2 registration custodians, 2 verification keys}; {2 registration custodians, 3 reproducer processes} |
| P1A | malicious bytes, anchor made after the compromise | {2 registration custodians, 3 reproducer processes}; {2 registration keys, 2 reproducer keys, fcpub}; {2 registration keys, 2 reproducer keys, 1 trust-state key, carrier}; {2 registration keys, 2 reproducer keys, 1 trust-state key, src1, src2}; {2 registration keys, 2 reproducer keys, 1 trust-state key, src1, desig2}; {2 registration keys, 2 reproducer keys, 1 trust-state key, src1, op1src}; {2 registration keys, 2 reproducer keys, 1 trust-state key, src2, desig1}; {2 registration keys, 2 reproducer keys, 1 trust-state key, src2, op1src}; {2 registration keys, 2 reproducer keys, 1 trust-state key, desig1, desig2}; {2 registration keys, 2 reproducer keys, 1 trust-state key, desig1, op1src}; {2 registration keys, 2 reproducer keys, 1 trust-state key, desig2, op1src} |
<!-- CS7:END CP-R6-CONTROLS -->

## 13. What remains a lower-trust input in CP-1, and why it is bounded

| Input | Decision it enters | Bound | Where |
|---|---|---|---|
| Both first-contact sources, their designation, or one of them with an operator reading it twice | first admission | the first-contact root, computed and executed equal | `32` §9 |
| A revocation issued within 24 hours before admission | first admission on a machine without the newer state | CUR-R1: 24 hours; any store holding the newer state refuses | `32` §8 |
| The local clock on a machine without any store | first-admission age; anchor validity | RS-2; machines with a store fail closed below the high-water | `24` §10 |
| Both supplier classes, hidden common provenance, both toolchain lineages, the compiler source | bytes | TB-S2″, TA-12″ (CP-ENV, CP-TOOLCHAIN) | `33` §8 |
| Two verification processes with the pipeline; an insider change accepted by honest verification | source, inputs and content | TB-4′, TB-4 | `30`, `34` |
| Two registration custodians with three reproducer processes | bytes | TB-S1 (CP-BYTES) | `30` §12 |
| Repository-delivered state at or below a valid anchor | C1–C2 within 90 days (CI 7 days) | RS-1 core | `24` |
| The operator at the local trust gate choosing among eligible releases the repository requests | project first use | RR-2′; the repository only requests | `35` §7 |
| Project overlay; subdirectory legacy writes | configuration; working tree | LR-4, strength vector; `18` §9.1 | `26` |

## 14. Attacks the architect ran against revision 7 before hand-off

| ID | Attack (candidate instance of the class) | Result on revision 7 | Evidence |
|---|---|---|---|
| A-R7-01 | The trust-state publication process composes codes over an authority signed by two trust-state keys, by one root key, or of an attacker lineage, and hands them to both custodians | custodians do not publish; a genuine admitter given the codes directly refuses (`FIRST_CONTACT_AUTHORITY_UNVERIFIED`); the revision-6-shaped control admits | FA7 S2 P |
| A-R7-02 | Two stolen trust-state keys sign a descendant that drops a published revocation | the custodians refuse to publish (`STATE_DROPS_REVOCATIONS`); key theft needs the registration and reproducer thresholds too | FA7 S2 P; CS7 CP-FC-KEY-THEFT |
| A-R7-03 | A replayed genuine code pair from months earlier naming a binary revoked since, on a workstation, a CI image and media | `FIRST_CONTACT_STATE_TOO_OLD` on every path; with the age rule off the malicious binary is admitted (rule load-bearing) | CUR7 R, A08 |
| A-R7-04 | Re-admission with a value within 24 hours but below the store's state, and with a revocation the selected state lacks | `READMISSION_STATE_BELOW_HELD`; `BINARY_REVOKED_IN_HELD_STATE`; the ignore-store mutant admits | CUR7 A02 |
| A-R7-05 | A revocation issued 6 hours before a first install that both sources do not yet show | admitted: exactly CUR-R1; the same value after the ceiling, or on a machine holding the newer state, refuses | CUR7 W; CS7 CP-REVOKED |
| A-R7-06 | Same-account code plants an admission record, anchor, project record and confirmation before a genuine first admission | the protected store decides; the account store is moved aside; the revision-6 reading keeps the planted artefacts | ADM7 A07 |
| A-R7-07 | Clock set back 395 days on anchored machines with newer states delivered or withheld (the revision-6 oracle admitted a revoked release at C1) | `TRUST_CLOCK_BELOW_HIGH_WATER`: C0-R only; R-CLK-1 added in this revision after BA11r7 showed the rows | BA11r7; ADM7 CLK |
| A-R7-08 | A human confirmation naming an old state while the sources publish a newer one (the revision-6 oracle allowed C3) | no C3: currency is the state both sources publish | BA11r7 |
| A-R7-09 | A pipeline manifest carrying an injected C runtime object for one class and for both; a lock with inline content; a manifest-named key; two labels over one supplier; a relabelled toolchain lineage | `ENVIRONMENT_MANIFEST_NOT_DERIVED` ×3; `ENVIRONMENT_ASSEMBLY_NONCONFORMANT`; `ENVIRONMENT_COMPONENT_UNVERIFIED`; `ENVIRONMENT_DIVERSITY_NOT_MET`; `TOOLCHAIN_DIVERSITY_NOT_MET`; label-counting controls accept injected code | ENV7 (real `rustc 1.98.1`) |
| A-R7-10 | The same instrumented selection made by a lock change in reviewed source | registered and accepted: the source route TB-4/TB-4′, not a new selector | ENV7 A07b control |
| A-R7-11 | A renderer that classifies atoms by name prefix | the atom-level check fails on the committed results; the injective renderer passes | `statements_check.py` S3 |
| A-R7-12 | A register without the designation, publication-process, submitter or manifest-author inputs, without a schema field, or with a selector lacking an establishing party | `register_check.py` C9/C10/C3 fail | DA09r7 |
| A-R7-13 | Every excluded mode presented to the executor, schemas and calculator | refused or absent under every declared mechanism | PROF7 |
| A-R7-14 | The calculator on the concrete profile with the revision-6 enumeration | eight configurations did not finish in 90 seconds; the incremental enumeration finishes in under 2 seconds and equals the reference wherever the reference finishes | CS7 `enumeration_reference_checks` |
| A-R7-15 | A crash after each layout-migration step and RoT-1 `init` over an overlay | never `ABSENT` or `PARTIAL` after recovery; rolled-back trees byte-equal to the legacy project; `init` never over an overlay | crashmig7 |
