# 03 — Residual determinations (review r7 B, AR-0020)

Every residual that CP-1 declares in the trust and security scope gets a determination here. The sources are `35` §7, `32` §12,
`31` §9, `24` §10, `25` §10, `30` §12 and `33` §8. Documentation alone is not a bound.

## Criteria

The criteria are review r6 synthesis D `05-RESIDUALS.md`, unchanged.

**ACCEPTED** requires one of the following.

- **R-1:** the trigger needs a capability the trust model excludes, and the exclusion holds for the machine class as prescribed.
- **R-2:** all of these hold:
  - (a) no reasonable design under the chosen assumptions removes or bounds it;
  - (b) the bound is stated exactly;
  - (c) no surface presents the state as stronger;
  - (d) an acceptance test fails when the bound is exceeded.

**ACCEPTED WITH CONDITION** names the carried requirement that must hold. **NOT ACCEPTED** names the finding.

An owner-selected parameter is not reopened. A residual that follows from an owner selection is accepted when its consequence is
stated exactly.

## First contact and admission

| ID | Residual (as declared) | Attacks | Determination |
|---|---|---|---|
| **FC-R1′ / AD-1″** | The first-contact root: exactly the eight sets of CP-FC-ROOT (no key) | FA7 S3 (re-run byte-identical); RV7-B-A03 | **NOT ACCEPTED as stated** (RV7-B-M1). R-2 (b) fails: when both source identities arrive in one onboarding record, `{onboard}` is a minimal set the eight pairs do not show. The pairs are exact only if the two identities reach the operator through independent channels, and no rule requires that. The residual itself (a human must know where the owner publishes) is core. |
| FC-R2′ | An operator who types one source's values for both (`op1src`) | FA7 S2 D (re-run) | **ACCEPTED** (R-2): inside the root; `gov-admit` shows both sources used; RT-184 |
| FC-R3′ | An operator directed to look-alike sources (`desig1`, `desig2`) | RV7-B-A03 | **NOT ACCEPTED as stated** (RV7-B-M1): one designation input, not two |
| FC-R5 | Key theft at first contact: CP-FC-KEY-THEFT | BA12r7 (re-run byte-identical); RV7-B-A01-VB | **ACCEPTED** (R-2) for malicious bytes (G_BYTES). Separately, the trust-state threshold with the publication process admits a *revoked* binary (G_REVOKED), which CP-FC-KEY-THEFT and CP-REVOKED omit: RV7-B-H1 |
| **CUR-R1** | A revocation within the 24 hours before admission (`{win}`, 24 hours) | CUR7 W (re-run byte-identical); RV7-B-A01 | **NOT ACCEPTED** (RV7-B-H1). R-2 (b) fails: the bound is the listing delay plus 24 hours, and no rule bounds the delay (executed: admitted with the revocation 342 h old). R-2 (a) fails: first-hand establishment of the listing bounds it. |
| RS-2 | A machine without any store, stored codes, and a clock set back (`{stored_old, clockback}`) | CUR7 A08 (re-run) | **ACCEPTED** (R-1/R-2): TA-7 on machines without a store; machines with a store fail closed (R-CLK-1; ADM7 CLK re-run) |
| TB-1′ | A malicious binary run directly, outside admission | FA7 S1 | **ACCEPTED** (R-1). No first-install step runs a candidate (EX-24; R-FCD-2). |
| AD-2′ | Same-account code before first admission | ADM7 A07 (re-run byte-identical) | **ACCEPTED** (R-2): the protected store decides first admission; planted artefacts are moved aside |
| VR-B1′ | Same-account replacement of a user-writable binary | UW6 (re-run byte-identical) | **ACCEPTED** (R-1) |
| TB-L4 | Machines without stores lack an accepted-TBM high-water | CUR7 A04 (re-run) | **ACCEPTED** (R-2): `min_binary_version`, the security minimum, AP-R6 and GB-7 |

## Running machines: anchoring and currency

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| RS-1 | A machine anchored before a revocation that never receives later metadata | BA11r7 (re-run byte-identical); RV7-B-A02 | **ACCEPTED** (R-2) for C1–C2 within anchor validity (90 days; CI 7 days), never shown `current`. The "never C3 without a proof of at most 24 hours" part holds only for the age of the proof event: see RS-1b. |
| **RS-1b** | A C3 decision whose proof is a recent anchoring event can be stale by up to 24 hours | RV7-B-A02 | **NOT ACCEPTED** (RV7-B-H2). R-2 (b) fails: a proof event of at most 24 hours can name a state of any age (executed: a 4-month-old state, C3 `ALLOWED`). R-2 (c) fails: shown as "state published as of" the event time. R-2 (a) fails: a compiled state age at C3 bounds it. |
| RS-1c | A valid pin provisioned before a revocation | RV7-B-A02 (CI row) | **ACCEPTED** for C1–C2 (R-2). **NOT ACCEPTED** for its C3 statement in `24` §5.2: a re-stamped pin gives C3 on a state 6 days old (RV7-B-H2). |
| RS-2b | A restored store, the clock set back into its range, and every later statement withheld | BA11r7 CLOCK rows (re-run) | **ACCEPTED** (R-2): 90-day bound; RT-178 |
| RS-3 | A3 deletes or rewrites its own account store | ADM7 (re-run) | **ACCEPTED WITH CONDITION** CR4-B-01 (carried, unchanged) |
| RS-4 | Pins provisioned by a party the repository writer controls | CS7 CIR `pinprov` | **ACCEPTED** as scoping (TA-9). As review r6 D stated, the scoping does not cover an honest provisioner re-using a stored code (RV7-B-H2). |
| RS-5 | Witness-key compromise | PROF7 EX-01 (re-run; mutation-sensitive, RV7-B-A08) | **REMOVED BY EXCLUSION** (verified) |
| TG-1, TG-2, TG-3 | Per-machine decisions; same-user PTY; non-trust gates | design | TG-1, TG-3 **ACCEPTED**; TG-2 **ACCEPTED WITH CONDITION** CR4-B-01 |

## Binary, registration, reproduction, environment

| ID | Residual | Determination |
|---|---|---|
| TB-S1 | Registration custodians at threshold with the reproducer quorum (CP-BYTES) | **ACCEPTED** (R-2): CS7 and BA12r7 re-run byte-identical; OP-9 (b) + (d) is the owner's selection. Its revocation remedy depends on RV7-B-H1's correction. |
| TB-S1 (environment) | Environment reproducers at the quorum | **ACCEPTED** (R-2): R-BENV-7″ conflict refusal (ENV7 T1 re-run byte-identical with the real `rustc 1.98.1`) |
| **TB-S2″** | Both supplier classes, or hidden common provenance (`{env_common}`) | **ACCEPTED WITH CONDITION** CR7-B-01 (RV7-B-L1). The singleton `{env_common}` is inherent to OP-16 (b). Its bound (R-2 (b)) depends on what "independent provenance" means in the registry, and today that is string inequality. |
| TA-12″ | Both toolchain lineages, or the compiler source (`{tc_src}`) | **ACCEPTED** (R-2) as the owner's OP-10 (b) consequence. No lineage is evidenced (OT-2), so no target is certified (CC-3), and nothing relies on it. |
| TB-S3 | Common custody of reproducers, environment reproducers or registration custodians | **ACCEPTED** (procedural; RT-180) |
| TB-4, TB-4′ | An insider change accepted by honest verification; two verification processes with pipeline input | **ACCEPTED** (R-2): CP-SRC; RV7-B-I1 notes that OP-8 independence rests on key custody |
| AV-S1 | One reproducer key forces a conflict | **ACCEPTED** (R-2): registration revocation remedy (FA7 S5 re-run) |
| RR-2′ | At a project's first use, the operator confirms an eligible release that the repository requests | **ACCEPTED** (R-2): the gate shows the newest eligible release known and the repository only requests (OP-11 (b)). The eligible set is as correct as the negatives held (RV7-B-H1). |
| A8 | Root threshold compromise | **ACCEPTED** (R-1): outside TA-4 |

## Owner trade-offs (not residuals; assessed in `00-REPORT.md` §7)

- OT-1 is real and bounded, and is a genuine owner trade-off. It is stated incompletely (RV7-B-L4).
- OT-2 is real and bounded. It is not a new owner trade-off: the owner text already decides "not certified rather than silently
  falling back".

## Summary

| Determination | Residuals |
|---|---|
| **NOT ACCEPTED** | FC-R1′/AD-1″ and FC-R3′ as stated (RV7-B-M1); CUR-R1 (RV7-B-H1); RS-1b and the C3 part of RS-1c (RV7-B-H2) |
| ACCEPTED WITH CONDITION | TB-S2″ (CR7-B-01); RS-3, TG-2 (CR4-B-01) |
| ACCEPTED | FC-R2′, FC-R5 (G_BYTES), RS-2, RS-2b, RS-1 (C1–C2), RS-1c (C1–C2), RS-4 (scoping), TB-1′, AD-2′, VR-B1′, TB-L4, TB-S1, TB-S1 (environment), TA-12″, TB-S3, TB-4, TB-4′, AV-S1, RR-2′, A8, TG-1, TG-3 |
| REMOVED BY EXCLUSION | RS-5 |
