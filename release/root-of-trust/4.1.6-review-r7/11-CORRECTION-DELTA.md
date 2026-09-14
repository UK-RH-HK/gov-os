# 11 — Architectural correction delta (RoT-1 revision 7, CP-1)

This delta is architectural only. It is not a patch list and implements nothing. The product owner has frozen the Root-of-Trust
revision loop after this verdict (HO-0022 §0), so the delta is recorded as **evidence for the later meta-architecture review**; it is
not routed to another revision. For each blocking class it states the unestablished invariant, the kind of fix (HO-0022 §2a), what
would close it, and the evidence a re-review would require.

D-0008 and ARCH-0002 remain PROPOSED (`PROVISIONAL`, `human_approved: false`, `in_effect: false`); D-0007 remains ACTIVE. Nothing here
approves anything.

## Routing

| Class | Findings | Remainder of, or new | Unestablished root invariant (short) | Kind of fix | Route |
|---|---|---|---|---|---|
| **BC7-1** First-contact restrictive-fact listing | RV7-H1 | **Narrowed remainder of BC6-2** (first-contact currency) applied to negative and minimum-raising facts, intersecting **BC6-4** (no establishing party for listing completeness; no calculator strategy). The instances (omission, not replay or drop) are new; the class is not. | Every restrictive fact issued by its dedicated authority (a revocation of a binary, registration or admitter; a security-relevant registration) takes effect at first contact within a stated, enforced bound, established first-hand by a party the root counts; the trust-state authority or its publication process cannot suppress it by omission. | **ENGINEERING_CORRECTION** | architect |
| **BC7-2** Running-machine currency of the named state | RV7-H2 | **Narrowed remainder of BC6-2** on the running path, and of **R2-H2** (stateless-verifier currency). The instances (stored, re-stamped, media codes at C3) are new; the class is not. Also a deviation from OWNER-DESIGN-REQUIREMENTS-0002 OT-1. | Every C3 decision uses a Trust State whose own issuance is within the compiled production-currency ceiling (24 h) of the decision clock, in addition to naming the effective state; no stored, replayed, re-stamped or media value gives C3 on an older state. | **ENGINEERING_CORRECTION** (the owner decided the parameter and its media consequence in -0002) | architect |
| **BC7-3** Stated consequences and certification criteria not derived from normative rules and established facts | RV7-M1, RV7-M2, RV7-M3; the false statements of RV7-H1, RV7-H2, RV7-M4 | **Remainder of BC6-4** (statements from a model whose atoms or rules the normative text does not have), with **BC6-1**'s designation remainder (RV7-M1). **Materially new component:** the OT-2 certification criterion (RV7-M2) under the owner resolution received after revision 7. | Every stated residual bound and minimal set is computed from rules present in normative text over atoms that match the delivery rules; every certification criterion is an executable, non-circular procedure whose independence facts rest on verifiable provenance evidence, never on labels. | **ENGINEERING_CORRECTION**; an owner confirmation only if the architect retains a single designation input as a stated root atom instead of independent designation (CD7-3 (1)) | architect (then owner only in that case) |
| **BC7-4** Clean CI runner governed use | RV7-M4 | **Materially new** (a real combination of OP-3 Mode A, OP-11 (b) and the HO-0001 §3.2 clean-runner class that no earlier review attacked) | Every machine class's stated reachable operation classes are reachable under the gate rules; a clean runner's first governed use of a project has a selection mechanism the owner's gating rules allow, or the profile states that runners do no governed project work. | **ENGINEERING_CORRECTION**, with a possible **owner confirmation** (CD7-4) | architect, then owner if the chosen mechanism is a provisioned (non-interactive) selection |

Each blocking class is the recurring rejection class, **a lower-trust input yielding a current, higher-trust fact**, except BC7-4,
which fails closed:

| Class | Lower-trust input | Higher-trust fact obtained |
|---|---|---|
| BC7-1 | the trust-state publication process (rank 3), or at most the trust-state threshold (a purpose OP-4 separates from revocation) | a revoked binary or admitter as the current TCB of a first-install, CI-image or re-admitted machine; a superseded release as eligible |
| BC7-2 | a stored, replayed or re-stamped state code, or stale offline media (rank 5) | C3 currency "published as of now" on a state of any age within anchor validity; a revoked release installed |
| BC7-3 | one onboarding document; free-text provenance labels; the calculator's unstated full-matrix build rule | the owner's view of the first-contact root, of toolchain and supplier independence, and of the build-residual bounds; a future CERTIFIED label |
| BC7-4 | — (availability) | — |

**Unavoidable core versus these classes.** A machine cannot know metadata it never received; a first-contact operator must know
where the owner publishes; OP-7 (a) lets an anchored machine run C1–C2 for up to 90 days (CI 7) without newer metadata. Those are
core and stated (RS-1, TA-5′). They are not these findings. The findings are: an omission by a party other than the issuing
authority that has no bound; a stored or media value of unbounded age selecting C3 currency; and stated bounds computed from atoms
or rules that the text does not have.

## CD7-0 — Retain (confirmed by reproduction)

- **BC6-1 closures as stated.** The First-Contact Authority record at root threshold; compiled quorum and lineage in every admitter
  build; custodians publish only first-hand-verified statements and refuse drops; no composer, printer, submitter or platform root.
  Evidence: FA7 ×2, CUR7, PROF7 byte-identical; RV7-B-A01 controls.
- **BC6-2 closures as stated.** FC-9 compiled 24-hour admission age for replayed, stored, media, CI and designated values;
  re-admission applies both stores (AP-R1…AP-R6); accepted-TBM high-water at re-admission and use. Evidence: CUR7 and cur7x M2
  byte-identical.
- **BC6-3 closed.** Derived environment manifests from the lock in registered source, pinned supplier keys, agreeing environment
  reproductions and the registration over the exact identity; ENV7 byte-identical with the real `rustc 1.98.1`.
- **BC6-4 narrowed.** Register C9–C11, DA09r7 (578 fields), DA04r7 15/15, DA06r7, STATEMENTS-CHECK byte-identical.
- **Profile conformance and exclusions.** PROF7 113/113 checks and 24/24 exclusions byte-identical; RV7-B-A08 mutation sensitivity
  reproduced (the two schema mutations fail exactly EX-01 and EX-04: 111/113 checks, 22/24 exclusions); RV7-B-A09 schema sweep
  byte-identical; D-0008 has no `chosen_option`.
- **Key subsets below threshold.** BA12r7 byte-identical (0 accepts with ≤ 1 key).
- **Constitutional surface.** CSI self-test 78/78 byte-identical; checks exit 0 / 3 / 2 / 2 / 2; new files and keyed-member keys
  refused (RV7-D-A07 K1, K3).
- **Legacy containment.** R2-H4 closed as a class on the revision-7 layout (reviewer C `matrix7`, `struct7`, `gitops7`, `txn7`
  reproduced; `D-synthesis/01-REPRODUCTION.md`).

## CD7-1 — Restrictive facts at first contact established first-hand and bounded (closes BC7-1: RV7-H1)

**Mistaken equivalence.** *"A state that drops nothing the custodian published lists every restrictive fact issued."* Revision 7 bounds
the age of the state, not the completeness of what it lists.

**What would close it (engineering; the mechanism is the architect's choice).**
1. **First-hand negative and minimum facts at the sources.** Each source custodian receives, first-hand from the issuing authority,
   every revocation statement (binary, registration, final, candidate, admitter) and every registration, each carrying a strictly
   increasing per-authority sequence; a custodian refuses to publish a state code while a statement it holds, issued more than a
   compiled listing delay earlier, is not listed or referenced. Alternatively, the sources publish a code over the negative set and
   the security minimum that `gov-admit` requires as a selector, with the same compiled delay.
2. **Compiled bound.** The listing delay is compiled and no larger than the issuance cadence the 24-hour ceilings already require
   (RV7-L3), so CUR-R1's bound becomes "listing delay + 24 h", stated exactly.
3. **Both executors apply every held verified restrictive statement**, not only the listed ones (`17` S5 already states it for running
   machines).
4. **Register and calculator.** Name the establishing party of listing completeness (DR-18, the `revocations` and
   `revocation_statements` rows, the `registrations` row for AP-SEC). Add an omission strategy to CS7 for FA, RA_unheld, P1, P2 and
   CIR, for binaries, registrations, the admitter and the security minimum.
5. **Statements.** Regenerate CUR-R1, CP-REVOKED, CP-FC-KEY-THEFT (G_REVOKED), INV7-AGE, `24` §6 blast radius, `35` §3 and §7, and D-0008
   rules (7), (19) and (25) from the calculator.

**Not an owner trade-off.** OP-4 already separates the revocation authority; OP-7 (a) already implies a Trust State at least daily.
The coupling that first contact stops while a revocation is unlisted beyond the delay is the fail-closed consequence of those
selections and must be stated.

**Evidence a re-review would require.** RV7-B-A01 (a)–(c) and RV7-D-A01 on the corrected executor and custodian rule: the custodians
do not publish, or `gov-admit` refuses, for a revocation, an admitter revocation and a security-relevant registration older than the
stated delay, also with the statement withheld from the admitting machine; the calculator with the omission strategy reproduces the
restated blocks.

## CD7-2 — C3 currency bounded by the named state's age (closes BC7-2: RV7-H2)

**Mistaken equivalence.** *"A recent event that names the effective state is a recent state."*

**What would close it (engineering).**
1. Every C3 currency proof (R-CUR-1 pin or human confirmation; R-CUR-2 in-gate codes) additionally requires the named Trust State's
   `issued_at` to be no more than the compiled production-currency ceiling (24 h) before the decision clock, and not in the future
   beyond the skew, under R-CLK-1, exactly as FC-9 does at admission. `bootstrap.admission_ceilings.production_currency_hours` may only
   lower it.
2. State the consequences the owner already accepted in OWNER-DESIGN-REQUIREMENTS-0002: an air-gapped or long-offline machine needs a
   state at most 24 hours old for every C3 (media prepared within that window), and keeps C1–C2 within anchor validity (RV7-I3); a CI
   runner needs a state within 24 hours for gate-less C3 (`trust verify-artifact` acceptance).
3. Restate R-ANC-4, `24` §3.2, §4.4, §5.2, §6, §10 (RS-1b, RS-1c), `25` AP-3, `27` §3.1, `28` A-R7-08, `35` §2 (OP-7 row) and §3, and D-0008
   rules (7) and (19).
4. Replace BA11r7's `sources_latest` assumption with the rule, and compute G_REVOKED for P1, P2 and CIR with a stored-code atom.

**Evidence a re-review would require.** RV7-B-A02 part E and cur7x M3 on the corrected executor: `TRUST_STATE_CURRENCY_UNPROVEN` (or a
named code) for stored codes naming a state older than 24 hours, a re-stamped CI pin, and media codes 37 days old; honest in-window
proofs still `ALLOWED`; the calculator shows no C3 row on a state older than 24 hours; RV7-D-A06 mutant M01 is killed by a shared vector.

## CD7-3 — Statements and certification criteria from rules and evidence (closes BC7-3: RV7-M1, RV7-M2, RV7-M3)

1. **Designation (RV7-M1).** Either a rule that the two source identities reach operators through independent channels (for example,
   one from the organisation's ceremony record, one delivered with the separately custodied medium or by its custodian), each an atom;
   or a single designation atom in the stated root, computed, with the consequence shown to the owner. Restate CP-FC-ROOT, FC-R1′,
   FC-R3′, INV7-FC, `35` §7, `31` AD-1″ and D-0008 rule (25). If the architect retains the single atom, the owner must be told that one
   altered onboarding document suffices for a malicious first TCB with no key, and confirm.
2. **Certification criteria (RV7-M2), per OWNER-DESIGN-REQUIREMENTS-0002 OT-2.**
   - Define CC-3 as an executable procedure: the registered compiler source rebuilt through at least two toolchain lineages whose
     bootstrap chains are evidenced (registered and reproduced bootstrap releases down to a root that is not the upstream binary
     compiler archive), the resulting compilers used to build `gov` and `gov-admit` and compared bit for bit (diverse double
     compilation), with an evidence schema, the comparison rule, and the refusal code; the verifier and `draft-policy` refuse a
     lineage without `bootstrap_registration` evidence, and refuse a registry in which no lineage has one.
   - Independence facts are canonical identities with evidence (bootstrap root artefact digests, package-source and signing key
     fingerprints, build-system identities), disjoint across lineages and across supplier classes, never free text; a
     distribution or mirror of one lineage is not a second lineage.
   - Adopt the owner's label `NOT CERTIFIED — TOOLCHAIN ASSURANCE INCOMPLETE` in `35` §5 and `profile/CP-1.yaml`; restate `21` §2 and
     `35` §6 as resolved by -0002 (OT-1, OT-2) and D-0008 rules (26), (30) and (31).
3. **Cross-axis reproduction (RV7-M3).** Either a normative coverage rule (the matching reproductions and the custodians' own
   reproductions together cover every registered (supplier class × toolchain lineage) combination for the target, and acceptance
   refuses otherwise), or restated residuals TB-S2″ and TA-12″, blocks CP-TOOLCHAIN and CP-ENV and `21` §4 that include the cross pairs,
   computed with one build per party as the text permits. Joint goal in CS7 (toolchain and environment atoms together); ENV7's
   `acceptance` builds only the combinations the rules require.
4. **Derived statements.** Every consequence block cited by the owner options is regenerated after 1–3 and CD7-1/CD7-2; the register
   names the designation delivery, listing completeness and reproduction coverage as inputs with establishing parties.

**Kind.** ENGINEERING_CORRECTION. OT-2 is decided by the owner (no certified target until the criterion is evidenced; no fallback;
not labels). OP-10 (b) and OP-16 (b) are not reopened.

**Evidence a re-review would require.** RV7-B-CS7 A03 with the corrected designation rule; RV7-D-A03 and RV7-B-A04 refused
(`TOOLCHAIN_DIVERSITY_NOT_MET` / `ENVIRONMENT_DIVERSITY_NOT_MET` or a named evidence code); RV7-D-A02 parts E and C: the diagonal-only
reproduction set refused under the coverage rule, or the cross pairs present in the restated blocks.

## CD7-4 — Clean CI runner governed use (closes BC7-4: RV7-M4)

**What would close it.** The architecture states one mechanism by which a clean runner's first governed use of a project is
selected, and restates `24` §5.2, `06` §3, `27` §2–§3 and BA11r7 accordingly. Options, with consequences (not chosen here):

| Option | Mechanism | Consequence |
|---|---|---|
| CI-a | The runner image carries a per-project record (or selection) for each project it serves, provisioned at image build by the TA-9 operator naming the exact eligible release digest, at or above the security minimum, valid no longer than the image record (7 days) | CI works per project; image rebuild per release change; the selection is local-authority but not an interactive human gate |
| CI-b | `project_first_use` becomes pin-approvable for `ci` pins, bound to the exact release digest and minimum, ≤ 7 days, in the system pin directory under TA-9 | as CI-a without per-project images; widens the pin enum by one C3-carrying kind |
| CI-c | The profile states that clean runners do no governed project work (C0 for projects) | no CI governance under CP-1; no new selection authority |

**Owner confirmation.** OP-3 Mode A requires a local human trust gate for "adoption; production installation; update; rollback;
downgrade/recovery". Whether a provisioned CI selection (CI-a, CI-b) is compatible with that text is for the owner to confirm if the
architect chooses one of them; CI-c needs no owner decision.

**Evidence a re-review would require.** A clean-runner vector (no record, no terminal, valid CI pin) reaching exactly the classes the
restated text claims; BA11r7's M2 rows evaluated with the gate.

## 5. Rule text affected (D-0008 and ARCH-0002 stay PROPOSED)

| Rule | Class | Change required |
|---|---|---|
| (7) | CD7-1, CD7-2 | currency for installation, update, rollback and ingress needs a named state within 24 hours, not only a proof event; restrictive facts apply within a stated listing bound |
| (19) | CD7-1, CD7-2 | first admission never selects a state missing a restrictive fact older than the listing bound; no trust ingress on a state older than 24 hours |
| (22) | CD7-1, CD7-3 | the register names listing completeness, designation delivery and reproduction coverage; the calculator carries the omission, stored-code, onboarding and cross-axis strategies |
| (25) | CD7-1, CD7-3 | the first-contact root restated from the calculator with the designation rule and the omission strategy |
| (26) | CD7-3 | supplier-class and toolchain-lineage independence from canonical, evidenced identities; reproduction coverage |
| (30) | CD7-3 | certification needs the executable CC-3 procedure; the owner's label |
| (31) | CD7-3 | OT-1 and OT-2 recorded as resolved by OWNER-DESIGN-REQUIREMENTS-0002, not as open trade-offs |
| (18), (23) | CD7-4 | the clean-runner selection mechanism, if CI-a or CI-b |

## 6. Non-blocking items to carry

Each is a bound, testable requirement. "CR7-B-nn" and "CR7-C-n" are reviewer B's and C's `04-CARRIED-REQUIREMENTS.md`.

| Item | Requirement | Acceptance test |
|---|---|---|
| RV7-M5 | CR7-C-1, strengthened: a first admission reads every surviving account-store floor and negative as restrictors (never as authority) before the move-aside and writes their maxima and unions into the new protected store; a surviving higher account-store state that the admission's selected state is below is refused, never silently discarded; the account(s) moved aside are named | `adm7x` X2 on the implementation: after protected-store loss with the home kept, the next admission keeps the high-water; a lower state within 24 hours is refused (`READMISSION_STATE_BELOW_HELD`); pending obligations survive |
| RV7-M6 | CR7-C-2 | `ident7` / RT-196 over real Git relocations (including `cp -r`, `tar`, re-clone at the same path) |
| RV7-M7 | CR7-C-3 | RT-16 / RT-195 crash before the per-project record exists; `gov recover` honours the journal |
| RV7-M8 | CR7-C-4 | RT-195 with `git clean -fdx` in the crash window; `init` loses no classification |
| RV7-M9 | CR7-C-5 | RT-195 crash after `RENAME_EXCHANGE`; recovery completes (executed) or rolls back |
| RV7-M10 | **CR7-D-01.** The shared conformance vectors (`31` R-ADM-14, `35` CC-8) include a vector that kills each surviving mutant of RV7-D-A06 on both executors: C3 proof naming a non-effective state; account-store floors; the two state codes disagreeing at the admitter; AP-7; FCA threshold under the named root version; clock skew beyond 300 s; admitter revoked in the selected state; registration equivocation | RV7-D-A06 re-run against the implementation's executors and vectors: 22 of 22 detected |
| RV7-L1 | CR7-B-02 | RV7-B-A05 on the implementation's schema and `draft-policy` |
| RV7-L2 | CR7-B-03 | as CR7-B-03 |
| RV7-L3 | CR7-B-04 (a stated issuance and two-source publication cadence of at most 24 hours; the failure surface) | as CR7-B-04 |
| RV7-L4 | CR7-B-05 | a clean re-run of the committed runner from a fresh export: exit 0, byte-identical except declared run-dependent leaves |
| RV7-L5 | CR7-B-07 | as CR7-B-07 |
| RV7-L6 | CR7-C-6 | `txn7` on the implementation |
| RV7-L7 | CR7-C-7 | `adm7x` X4 on the implementation |
| RV7-L8 | CR7-C-8 | `adm7x` X5 on the implementation: 0 torn reads |
| RV7-L9 | **CR7-D-02.** `clock_reset` applies once, only from a Trust Policy that is effective at ingest and newer than the held policy version, and lowers only high-water values recorded before that policy's `issued_at`; a replayed or superseded policy's reset is ignored; the executors implement it and a vector tests it | RV7-D-A05's two cases on the implementation: a replayed older policy leaves the high-water at 1000; an effective reset does not keep lowering values recorded after its issuance |
| RV7-L10 | **CR7-D-03.** The operator procedure for air-gapped admission and in-gate state codes states that the authenticated private release channel's codes are read on a connected device independently of the media, and that the media carry only the mirror source | procedure review; a vector in which both typed codes come from one medium is recorded as `op1src` and the procedure text names it |
| RV7-L11 | CR4-B-05 (carried) plus **CR7-D-04**: no wildcard leaf rule of class `informational` or `project_tunable` covers a subtree whose new keys a compiled consumer could read; a new key under such a subtree is unclassified (exit 2) unless the inventory names it | RV7-D-A07 K2 on the implementation's checker: exit 2 |
| RV7-L12 | CR6-B-04 / RT-198 | RT-198 |
| RV7-I1 | CR7-B-06 | as CR7-B-06 |
| RV7-I3 | the D-0008 ratification package states the OT-1 reading (C1–C2 within anchor validity; C3 on a state within 24 hours) | text review |
| RV7-I4 | `17` rows for excluded modes moved to non-production history | text review; PROF7 unchanged |
| earlier carried | CR4-B-01, CR4-B-04, CR4-B-05; C-2 … C-6; CR6-C-1 … CR6-C-12 not closed above | as earlier reviews |

## 7. Re-review entry criteria (recorded; the loop is frozen)

1. **Classes closed.** CD7-1 … CD7-4 closed as classes in the pack, the schemas, the register, the calculator, D-0008 and ARCH-0002
   (PROPOSED, not active).
2. **Evidence re-run against the corrected rules.**
   - (a) RV7-B-A01, RV7-B-A01m and RV7-D-A01 (omission of binary revocation, admitter revocation, security-relevant registration).
   - (b) RV7-B-A02 part E and C, cur7x M3, and RV7-D-A10 (stored, re-stamped and media codes at C3).
   - (c) RV7-B-CS7 (A01-VA/VB, A02, A03) and the calculator with the omission, stored-code, onboarding and cross-axis strategies.
   - (d) RV7-D-A02 (parts E, R and C) and RV7-D-A03, RV7-B-A04.
   - (e) A clean-runner vector for CD7-4.
   - (f) Unchanged in what they refuse: FA7, CUR7, ADM7, ENV7, PROF7, BA11r7 (with the rule), BA12r7, PPR7, DA05r7, DA06r7, DA09r7,
     DA04r7, REGISTER-CHECK, STATEMENTS-CHECK, CSI self-test and checks; reviewer C's `matrix7` (R2-H4 0 violations, LP-1r 0 project
     writes), `struct7`, `gitops7`, `txn7`.
   - (g) RV7-D-A06 against the corrected executor and vectors: every mutant detected.
3. **Response matrix** over RV7-H1 … RV7-I6, CR7-B-01 … CR7-B-07, CR7-C-1 … CR7-C-9, CR7-D-01 … CR7-D-04 and CD7-0 … CD7-4, with no
   "resolved" claim resting on untested evidence.
4. **Owner package.** OT-1 and OT-2 recorded as resolved by OWNER-DESIGN-REQUIREMENTS-0002; every consequence block regenerated; the
   CD7-3 (1) and CD7-4 owner confirmations presented only if the architect's choice requires them; no owner parameter reopened; no
   choice made for the owner.
