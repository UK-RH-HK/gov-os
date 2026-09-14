# 04 — Owner requirements, owner resolutions and owner options (synthesis D, AR-0022)

The owner texts are read verbatim: OWNER-DESIGN-REQUIREMENTS-0001 (`c85d80c2…`) and OWNER-DESIGN-REQUIREMENTS-0002 (`91472048…`), both
binding. Revision 7 (`d07d200`) predates -0002; the acceptance rule applies -0002 regardless (HO-0022 §2b).

## 1. HO-0001 §3 requirements, judged as classes

| Requirement | Determination | Holds (decisive evidence) | Fails |
|---|---|---|---|
| **§3.1** Constitutional-floor closure | **SATISFIED** | CSI self-test 78/78 byte-identical; checks exit 0 (framework), 3 (4.1.5), 2 (4.1.2–4.1.4); non-first-hand registration refused (CON6 retained, B re-run); RV5-D-A05 and RV6-D-A03 (new Gate W and G0–G6 files) re-run by B byte-identical; RV7-D-A07 K1 (new artifact-flow policy, capability-contract Markdown and YAML) exit 2, K3 (new key in a keyed collection member) exit 2 | Carried, not class-breaking: RV7-L11 (a wildcard `informational` subtree accepts new keys; CR4-B-05), RV7-L12 (RT-198) |
| **§3.2** New-machine trust bootstrap | **NOT SATISFIED** | Unanchored machines C0; expiry to C0; R-CLK-1; admission 24-hour state age for replayed, stored, media and CI values; re-admission applies both stores; no surface prints `current` (BA11r7, ADM7, CUR7 reproduced); two machines at different epochs | **First install, clean CI runner image build, re-admission over an older store:** a revoked binary or admitter, or a superseded release, admitted while Trust States omit the restrictive fact (RV7-H1). **Old epoch, restored, offline returning, air-gapped:** production C3 on a state of any age within anchor validity from stored, re-stamped or media codes (RV7-H2). **Clean CI runner:** the governed use claimed is unreachable (RV7-M4). "An attacker controlling transport or the repository must not be able to select an old signed trust state and thereby create a current trusted fact" fails for C3. |
| **§3.3** Binary and root authenticity | **SATISFIED** as a class | No accept with at most one key, nor with release and trust-state keys and infrastructure (BA12r7 reproduced); release-final threshold 2; registration 2-of-3 delegated; binaries by 2-of-3 reproducers with registered digests; first-contact authority record at root threshold; lineage compiled into every admitter; non-circular chain (`25` §6); derived environments (ENV7 reproduced with the real toolchain) | Blocking MEDIUMs on the honesty of its stated residuals and on the certification criterion, not on the threshold chain: RV7-M1 (designation), RV7-M2 (label-based independence; CC-3 not executable), RV7-M3 (cross-axis residual). Revocation effectiveness at first contact (RV7-H1) is judged under §3.2, as review r6 judged RV6-H2. |
| **§3.4** Legacy-binary damage containment | **SATISFIED** | reviewer C `matrix7` reproduced (R2-H4 0 violations; LP-1r 0 project writes; no write elevates a non-`COMPLETE` tree), `struct7` byte-identical, `gitops7` (45 operations) and `txn7` summary equal (`01-REPRODUCTION.md`) | Carried: RV7-M6 … M9, RV7-L6 |
| **§4** Forward-compatibility constraint | **SATISFIED** for classification and content selection | as §3.1; RV7-D-A07 | Carried: RV7-L11 (wildcard subtree); RV7-I6 (binding-group derivation, RT-182) |

## 2. OWNER-DESIGN-REQUIREMENTS-0001 conformance

| Owner selection | Result | Evidence |
|---|---|---|
| Option C; A, B, D, E, F not supported production alternatives | **conforms** | EX-22; D-0008 has no `chosen_option` |
| OP-1 root 3 keys, 2-of-3, three custodial roles, offline, root ceremony for policy and lineage changes | **conforms** in the compiled check; schema gap RV7-L1 | PROF7; RV7-B-A05 |
| OP-2 (b) delegated registration 2-of-3, single-purpose | **conforms** | PROF7 EX-09; `PURPOSE_SHAPE`, `WHITELIST` |
| OP-3 Mode A always_gate; local human trust gate; repository gate records are requests | **conforms**; the CI combination is unstated (RV7-M4) | PROF7 EX-06; pin enum excludes C3 kinds |
| OP-4 purposes (candidate separate; final ≥ 2; trust state 2-of-3; certification 2 records; revocation 2-of-3; retrieval separate; no witness; domain separation mechanically enforced) | shapes **conform**. **Deviation:** the dedicated revocation authority's effect at first contact is subordinate to trust-state listing that no rule establishes; the trust-state purpose can nullify the revocation purpose there (RV7-H1) | RV7-B-A01, RV7-D-A01 |
| OP-5 30-day warning, informational | **conforms** | PROF7 EX-07 (compiled read only by display) |
| OP-6 (a) once per verifier trust store | **conforms** | PROF7 EX-11 |
| OP-7 (a) anchored only; 90 d / 7 d; production install/update/rollback ≤ 24 h; expiry → C0; no stale state presented as current; high-water never backwards | anchors, expiry, R-CLK-1 and the admission path **conform**. **Deviation:** running-machine install, update and rollback accept a proof event ≤ 24 h naming a state of any age, shown "published as of" now (RV7-H2). High-water: protected-store loss discards a surviving account-store high-water (RV7-M5, carried). | BA11r7, ADM7, CUR7; RV7-B-A02; cur7x; adm7x |
| OP-8 = 2 independent verification records | **conforms** mechanically; independence rests on custody (RV7-I1) | PROF7 EX-13; FA7 R6 |
| OP-9 (b) 2-of-3 + (d) registered binary digests | **conforms**; its combination with OP-10 (b) and OP-16 (b) is stated incompletely (RV7-M3) | PROF7 EX-14; RV7-D-A02 |
| OP-10 (b) diverse, independently bootstrapped compiler agreement; independence by provenance, not filenames or mirrors; no silent fallback | rule present, no fallback, no certified target: **conforms in outcome**. **Deviation:** independence is defined by free-text strings; "not rooted in an upstream archive" is unchecked; two distributions of one lineage pass (RV7-M2) | RV7-D-A03 |
| OP-11 (b) raise the minimum at every security-relevant change; no grace; transport never chooses | **conforms** mechanically (E3′, AP-SEC, DR-25). **Deviation (part of RV7-H1):** the raise depends on a Trust State referencing the registration, with no bound | RV7-D-A01 |
| OP-12 (a) separate compiled admitter, registered and reproduced; helper-machine and script admission excluded | **conforms**; custodian verifier genesis unstated (RV7-L5) | PROF7 EX-02, EX-03; FA7 S1 |
| OP-13 (b) two owner-controlled sources, separate custody, byte-identical, both required; (c), platform root, (d)-only excluded; no single publisher composes | mechanism **conforms** (compiled quorum; EX-04, EX-05, EX-17, EX-18, EX-23). **Deviation in stated consequence:** one onboarding record designates both sources (RV7-M1); the air-gapped second-channel procedure is unstated (RV7-L10) | FA7; PROF7; RV7-B-CS7 A03 |
| OP-14 (b) all records expire; re-admission never lowers the high-water | expiry **conforms**; re-admission with both stores **conforms**; protected-store loss (RV7-M5, carried) | ADM7 X14; CUR7 A02; adm7x X2 |
| OP-15 (a) revoked binary read-only | **conforms** | ADM7 X15; PROF7 EX-20 |
| OP-16 (b) two independent supplier classes by provenance, not labels; static linking; narrow targets | mechanism **conforms** (derived manifests, pinned keys). **Deviation:** class independence is string inequality plus distinct key ids (RV7-M2, from RV7-B-L1) | RV7-B-A04 |
| First-contact composer/signer at root threshold | **conforms** | FA7 S2 P; R-FCA-1…4, R-FCS-1…3 |
| Build-environment manifest: no single author; deterministic; authoritative with reproductions and the 2-of-3 registration | **conforms** | ENV7 reproduced |
| Initial certified scope and exclusions (witness, helper machine, script, (c) either, platform root, mode B, clock or grace trust, unanchored mutation) | **conform**: absent or refused | PROF7 113/113 and 24/24 reproduced; RV7-B-A08, A09 reproduced; cur7x R6; RV7-I4 (text only) |
| D-0008 `PROVISIONAL` / `PROPOSED` / `human_approved: false`; D-0007 ACTIVE | **conforms** | `D-synthesis/evidence/outputs/RV7-D-A04.json` `decision_records` |

## 3. OWNER-DESIGN-REQUIREMENTS-0002 conformance

| Resolution | Result | Evidence |
|---|---|---|
| **OT-1 A** — immutable first-contact material (lineage, root fingerprints, admitter identity and digest, TBM identity, compiled policy identity) from both channels independently; one may be offline media | **conforms** at admission (FCA at root threshold, trust code from both sources, compiled lineage). Text gap: the air-gapped procedure does not say the private channel is read independently of the media (RV7-L10). | FA7; RV7-D-A08 |
| **OT-1 B** — current trust state under OP-7 (a): the anchor satisfies 24 h; no longer window for media; stale state on authentic media never current; high-water never lowered | admission (FC-9) **conforms**. **Deviation:** running-machine C3 on media or stored codes of any age within anchor validity (RV7-H2). High-water after protected-store loss (RV7-M5, carried). | cur7x M2, M3; RV7-B-A02 |
| **OT-1 B** — without fresh state: inspect first-contact material; bounded diagnostic level; no production admission/install, no C1–C3 on stale state | admission **conforms** (`FIRST_CONTACT_STATE_TOO_OLD`); C3 **deviates** (RV7-H2); C1–C2 on an anchored chain within OP-7 (a) validity is the owner's selection under the consistent reading (RV7-I3) | CUR7 A08; RV7-D-A09 |
| **OT-1** — no clock-based grace-period exception | **conforms** (EX-07) | PROF7 |
| **OT-2** — no interim certification; all targets NOT CERTIFIED until evidenced; no upstream-archive fallback | **conforms** (no target certified; first contact refuses; EX-15) | `35` §5; PROF7 EX-15 |
| **OT-2** — criterion explicit, executable/testable, non-circular; diversity genuine, not labels; "two distributions" and "two mirrors" are not independence | **NOT MET** (RV7-M2): CC-3 has no executable procedure; lineage independence is string inequality; the verifier accepts two distributions of one lineage | RV7-D-A03 |
| **OT-2** — label "NOT CERTIFIED — TOOLCHAIN ASSURANCE INCOMPLETE" | **NOT MET**: `NOT CERTIFIED — pending criteria` (RV7-M2) | `35` §5; `profile/CP-1.yaml` |
| Acceptance without a certified target, provided the criterion is explicit, executable/testable and non-circular | **precondition not met** (RV7-M2) | as above |

## 4. Owner options

| Question | Determination |
|---|---|
| Pre-decided? | **No.** D-0008 has no `chosen_option`; the architecture applies the owner's selections and states no own choice. |
| Complete? | **No.** The OP-3 Mode A × OP-11 (b) × clean-runner combination has no stated mechanism or consequence (RV7-M4). OT-1 and OT-2 are presented as open (`21` §2, `35` §6) although -0002 resolved them (the text predates -0002). |
| Honest about security consequences? | **No.** False or incomplete stated consequences: CUR-R1 and CP-REVOKED (RV7-H1); RS-1b, `24` §5.2, §6, A-R7-08 (RV7-H2); CP-FC-ROOT and D-0008 rule (25) (RV7-M1); CC-3 "never from labels" and rule (26) (RV7-M2); CP-TOOLCHAIN, CP-ENV, INV7-TC, INV7-ENV-B and `21` §4 (RV7-M3); `24` §5.2 CI C1–C2 (RV7-M4). OT-1's options were computed as "only the bound of `win`" changes, which RV7-H1 falsifies. |
| Reopened owner parameters? | **No** finding here reopens OP-1…OP-16. Every correction in `11` operates inside the selections. Two points need owner confirmation only if the architect chooses a mechanism that needs it: a single designation input kept as a stated root atom (CD7-3 (1)), and a provisioned CI selection under OP-3's "adoption" (CD7-4). |
| Genuinely new owner trade-off found? | **No.** Reviewer C's candidate (C1–C2 on an anchored chain) is covered by OP-7 (a) as clarified by -0002 (RV7-I3). Reviewer B's OT-1 trade-off was resolved by -0002 after B completed. |
