# 11 — Architectural correction delta (revision 4 → revision 5)

This delta is architectural only. It states each blocking **class**, the invariant that is not yet established, and what
would close it. It is not a patch list and implements nothing. Mechanisms are the next architect's choice; the next
reviewers will attack each class with new held-out attacks, not tick these items. The next architect receives the
completed findings (`10-BLOCKING-FINDINGS.md`) and this file.

D-0008 and ARCH-0002 remain PROPOSED. Nothing here approves them.

## CD4-0 — Retain (confirmed sound under reproduction)

- **Everything review r3 CD3-0 retained**, which this review did not contradict.
- **BC-1 closures (RV3-H1):** exact precedence registration (`precedence_unregistered`); precedence only from
  registrations; the two-directional order; the directed project join; required presence (`surface_required_missing`);
  one YAML profile; the Overlay Surface with default-deny migration targets; project strength over effective policy.
  P1r4 on real 4.1.5, CSI self-test 56/56 and the review-r3 lattice and removal probes reproduced.
- **BC-2 closures (RV3-H2):** inclusion anchors; mandatory pin validity; currency proofs for C3 and binary acceptance;
  the separate `freshness-witness` purpose with a compiled C3 threshold of 2; no `current` label; the pin integrity
  predicate. P4r4 (54 scenarios, 9 mutants) and B's independent 336-row matrix reproduced with 0 unstated rows.
- **BC-3 closure as stated (RV3-H3):** V8 source equality; `release-final` does not choose a binary's source. VA4
  reproduced.
- **Legacy containment for root-anchored invocations:** C's 2,504 `--root` invocations on three layout variants, 0 writes;
  LR-2's bounds on removal and Git restore.
- **Carried closures:** lift attestation (RV3-M1), far-future statements (RV3-M3), artefact playbook (RV3-M4), decision
  table for `INCOMPLETE` (RV3-L1), accepted-TBM high-water (RV3-M8), rotation re-signing (RV3-L8).

## CD4-1 — Independent decisions for the TCB (closes BC4-1: RV4-H1)

**Class.** The mistaken equivalence is *"several signatures over a binary ⇒ several independent judgements about it"*.
Custodians and the publisher re-check that an upstream attestation exists; the facts that make a binary the TCB are each
established by one threshold-1 key.

**Relation to earlier classes.** Narrowed remainder of R2-H3 / BC-3. The threshold-1 decision moved from `release-final`
to `build-attestation` and `verification-attestation`.

**Invariant not yet established.** Each fact that makes a binary the TCB — (a) these bytes are a faithful build of source
S, (b) S is the legitimately verified source — is established by independent parties at a threshold that `verify-artifact`
checks and that is at least as strong as the authority the binary carries. A signature counts toward that threshold only
if its signer attests a fact it established itself.

**What closes the class.**
1. **Bytes.** The faithful-build fact needs at least two independent establishments that the verifier checks: for example
   a compiled `build-attestation` threshold of at least 2 with disjoint custody, or `release-artifact` statements that
   assert the custodian's own reproduction. A custodial pre-check of upstream signatures adds no threshold.
2. **Source.** Under the architecture minimum, source legitimacy does not rest on one verification key: root-registered
   production sources, a verification threshold of at least 2, or a REJECTED-verdict path the pipeline cannot suppress.
3. **Minimum capability sets.** Re-derived with pipeline input counted on every route, for every OP-2 answer (source
   authority, `release-artifact` (i)–(iii), rebuilder count, verification threshold) and both OP-4 answers.
4. **Oracle.** No oracle row expects an attack to be `ACCEPTED`.

**Evidence required.** RV4-B-A01, A02 and the A06 enumeration (including OP-2 (iii), D-A07) re-run against the corrected
rules: no capability set below the stated minimum is accepted, and the stated minimum counts pipeline input.

## CD4-2 — Anchored, non-circular first TCB on every machine (closes BC4-2: RV4-H2)

**Class.** The mistaken equivalence is *"the chain is non-circular for binary N+1, therefore for the machine"*. The first
binary on a machine is accepted outside the anchor, negative-set and currency rules, by comparisons with values it prints,
and every first-install ceremony runs on it.

**Relation to earlier classes.** Narrowed remainder of R2-H2 / BC-2 (attacker-selected stale state becoming current on a
first-install machine) at its intersection with R2-H3 / BC-3 (non-circular binary chain). Instance not attacked before.

**Invariant not yet established.** Every TCB acceptance on a machine — the first binary, a CI runner image's binary, a
legacy consumer's first RoT-1 binary — applies the same anchored, negative-set-checked, currency-proven decision as
`verify-artifact`, over digests measured by code other than the binary under test. No ceremony whose purpose is TA-5 runs
on a binary that has not been so accepted.

**What closes the class.**
1. **One acceptance semantics.** First-binary acceptance has the A1–A9 semantics, including an inclusion anchor taken
   from the independent channel's current state fingerprint, the anchored chain's negative set and a currency proof,
   executed by tooling independent of the binary under test.
2. **External measurement.** A build-from-source path binds the checked-out tree to the attested `source_tree_digest` and
   the built binary's SHA-256 to the build attestation and artefact statement. No value the candidate binary reports is
   compared.
3. **Ceremony order.** `confirm-root`, `confirm-state`, in-gate fingerprints and trust-gate confirmations on a
   first-install machine run after acceptance, or with the independent tool; OP-6 states the dependency.
4. **Migration and CI.** `11` Phase 4 and runner-image provisioning use that procedure; no path accepts a binary on its own
   verdict. TA-1 and TB-1 are restated.

**Evidence required.** RV4-B-A03 (revoked binary; remediated compromise with root v1 metadata), RV4-B-A04 (moved tag),
the Phase 4 path, a CI image path and D-A04 (ceremonies on an unaccepted binary): each refused by the documented
procedure.

## CD4-3 — Release-scoped registration of non-orderable content (closes BC4-3: RV4-H3)

**Class.** The mistaken equivalence is *"a value registered as permitted ⇒ a value permitted for this release"*. Pinned
leaves, keyed-collection members, `pinned_file` paths (and owner-domain sets, RV4-L10) register permitted digests with no
relation to release sequence; a threshold-1 final chooses among them.

**Relation to earlier classes.** Narrowed remainder of R2-H1 / BC-1. Precedence and absence are closed; the remaining
lower-trust choice is among permitted non-orderable values.

**Invariant not yet established.** A registration fixes, for each release sequence, the effective value of every
constitutional leaf, member and file. Content registered only for an earlier sequence is never effective in a later one
except through a computed, cumulatively declared, per-project-gated reduction.

**What closes the class.**
1. **Binding.** Registrations of non-orderable content are bound to release identity or a sequence range; E7 and the
   effective value (`19` §5.2) use the set registered for the release's sequence.
2. **Reduction.** Registering a superseded value for a later sequence, or re-adding it, is a computed reduction that the
   `reductions` check reports, with `lowering_history` and the per-project gate.
3. **Legitimate retention.** Installed releases at their own sequence keep working without widening what later sequences
   may carry.
4. **Blast radius.** The `release-final` blast radius names the choice among registered non-orderable content and states
   that Git-delivered higher-sequence releases pass no gate (RV4-L8).

**Evidence required.** RV4-B-A08 with consumption on real 4.1.5 (the `ASIA…` file stays excluded) and D-A02 T1–T4:
refused by E7, or reported as a computed reduction and gated. The legitimate case, an installed 4.1.6 release at a newer
TPS, stays eligible.

## CD4-4 — Owner options and blast-radius statements restated from the corrected rules (closes BC4-4)

| Option or statement | Required restatement |
|---|---|
| OP-2 source authority (S0)–(S3), `release-artifact` (i)–(iii), rebuilder count, verification threshold | minimum capability sets from CD4-1 with pipeline input; (iii) stated as not protecting against malicious bytes for genuine source unless co-signers reproduce (D-A07); (S1) cost including the `production_sources[]` reduction rule, or the rule re-scoped (RV4-L9) |
| `release-final` blast radius (`05` §1, `21` OP-2) | choice among registered non-orderable content (CD4-3); no gate on Git-delivered use (RV4-L8) |
| OP-4 | a single statement with counts from CD4-1 (RV4-L7) |
| OP-6 | dependence of TA-5 on first-binary acceptance (CD4-2; D-A04) |
| OP-7 (a) | RS-2 as it holds: no rollback detection under (a), (b), (d) or without a VTS (RV4-M4) |
| OP-7 (c) | witness input and custody consequences (RV4-M3) |
| All | nothing decided; proposals labelled |

## 5. Rule text affected (D-0008 and ARCH-0002; to stay PROPOSED)

| Rule | Class | Change required |
|---|---|---|
| (6) | CD4-3 | values of non-orderable classes move down across release sequences only through a computed, gated reduction |
| (9) | CD4-1 | the TCB facts rest on independent, verifier-checked thresholds; downstream signatures attest what their signers established |
| (16), (19) | CD4-2 | first-binary acceptance is anchored, negative-set-checked and externally measured; no self-validation in migration |
| (17) | CD4-1 | "binary source" and "faithful build" are distinct facts with distinct, independent authorities |
| (10), (12) | RV4-M1 (carried) | scope stated for invocations rooted in subdirectories and inside the PPS |

## 6. Non-blocking items the next revision must carry or close

These do not change the verdict. Each is a bound, testable requirement.

| Item | Requirement | Acceptance test |
|---|---|---|
| RV4-M1 | (a) `COMPLETE` requires closed entry sets under `governance/trust/**`: top level ⊆ the RoT-1 set; `kernel/` equal to the release content set; `state/`, `root/`, `lineage/`, `profiles/` only statement entries. Otherwise `PARTIAL(foreign_trust_entry)` and doctor D033 CRITICAL. (b) RoT-1 root discovery is defined: the nearest ancestor holding `governance/trust/FORMAT` is the project; a command whose working directory is inside the PPS refuses; a nested `governance/framework.lock` anywhere in the project is reported and never operated as a separate project inside the PPS. (c) `26` §3, LP-1, rules (10) and (12) and LR-2 state the subdirectory trigger and its reachable outcome: nested legacy installs; legacy commands operational beneath them; kernel edits `KERNEL_TAMPERED`; overlay rewrites `COMPLETE`, reported where recorded, LR-4 elsewhere. | C `subdir_escape` and D-A01 N1, N1b, N2, N3 on the implementation: each resulting tree is `PARTIAL(foreign_trust_entry)` or reports the nested install; RT-50 and RT-50b run every register from `product/`, `spec/`, `governance/`, `governance/overlay/`, `governance/views/`, `governance/trust/`, `governance/trust/kernel/`, `governance/trust/state/`, `governance/framework.lock/` with no `--root` and assert no change under `governance/trust/**` is left `COMPLETE` |
| RV4-M2 | CR4-B-01 (allow-list confinement; TCB-location predicate; restated claims; CI `sudo` note) | as CR4-B-01 |
| RV4-M3 | CR4-B-02 (witness input from ceremony or channel; independent custody) | as CR4-B-02 |
| RV4-M4 | CR4-B-03 (RS-2 and OP-7 (a) restated); on stateful machines, the clock high-water may be raised by every ingested non-future statement | RV4-B-A13 on a clean runner and on a stateful machine; RT-56, RT-102 |
| RV4-M5 | CR4-B-04 (requirements computed from pre-transaction inputs when no record exists) | P1r4 M5 migration on a fresh clone: `OVERLAY_WEAKENING_GATE_REQUIRED` |
| RV4-M6 | the install transaction removes a pre-existing `.governance-runtime/` directory-ignore line before writing the child-glob rule, idempotently | RT-122 on a real legacy `.gitignore`: the idiom lists nothing; a fresh clone is `COMPLETE` |
| RV4-M7 | the conformance oracle and `12` contain a distinguishing scenario for each of the 20 mutants of D-A03, including the five with no RT (A8 candidate negative, A4b unreferenced attestation, inclusion without "held", witness naming a non-effective TSS, unreferenced lift attestation) and the two ambiguous ones (TPS prior chain, `op7_mode` a→c) | D-A03 re-run against the next oracle detects 20 of 20; the named RT rows exist with harm assertions |
| RV4-L1…L7 | CR4-B-05 … CR4-B-11 | as in B `04` |
| RV4-L8, RV4-L9 | CD4-4 text; RV4-L9 rule scope | option text review; RT-127 |
| RV4-L10 | owner-domain slots may declare binding groups confirmed and pinned as a set; the resolution of several valid `owner_constitutional_file` decision pins is defined (newest set only, or exact set match) | a contract Markdown of version N with a compiled YAML of version N-1 is refused on a confirmed machine and on a pinned machine |
| C-2 … C-6 | as reviewer C `04` | as reviewer C `04` |

## 7. Re-review entry criteria

1. **Classes closed.** CD4-1 … CD4-4 are closed as classes in the pack, schemas, D-0008 and ARCH-0002, which stay PROPOSED
   and not active.
2. **Evidence re-run against the revision-5 rules.**
   - Reviewer B's `BC` enumeration, AF1–AF3 and `FB` constructions, and D-A07: no accepted set below the stated minimum;
     first-binary paths refuse revoked, remediated and moved-tag binaries.
   - Reviewer B's part P on real 4.1.5 and D-A02 T1–T4: refused or gated.
   - Reviewer C's `subdir_escape` and matrix positions, and D-A01 N1–N3, against the corrected state predicate.
   - D-A03 and D-A03b against the next oracle.
   - P1r4, P4r4, VA4 and the CSI self-test unchanged in what they already refuse.
3. **Response matrix.** It covers RV4-H1 … RV4-I1, CR4-B-01 … CR4-B-11, C's requirements and CD4-0 … CD4-4, with no
   "resolved" claim resting on untested evidence.
4. **Oracle.** No expected-`ACCEPTED` row is an attack, and every oracle mutant, including D-A03's, has a distinguishing
   scenario.
