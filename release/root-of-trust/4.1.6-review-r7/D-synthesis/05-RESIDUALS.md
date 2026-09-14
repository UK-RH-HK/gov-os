# 05 — Residual determinations (synthesis D, AR-0022)

Every residual that revision 7 declares gets a final determination here. Sources: `35` §7, `32` §12, `31` §9, `24` §10, `25` §10,
`30` §12, `33` §8, `26` §8, `20` §10, `23` §10, `27` §7. Documentation alone is not a bound (HO-0022 §3).

## Criteria

The criteria are those of review r6 synthesis D, restated.

- **ACCEPTED** only if either:
  - **R-1:** the trigger needs a capability the trust model excludes, and the exclusion holds for the machine class as prescribed; or
  - **R-2:** all hold: (a) no reasonable design under the chosen assumptions removes or bounds it; (b) the bound is stated exactly;
    (c) no surface presents the state as stronger; (d) an acceptance test fails when the bound is exceeded.
- **ACCEPTED WITH CONDITION** names the carried requirement that must hold.
- **NOT ACCEPTED** names the finding.
- A residual that follows from an owner selection is accepted when its consequence is stated exactly; the parameter is not reopened.

## First contact and admission

| ID | Residual (as declared) | Attacks | Determination |
|---|---|---|---|
| **FC-R1′ / AD-1″** | The first-contact root: exactly the eight sets of CP-FC-ROOT (no key) | FA7 S3 (reproduced); RV7-B-A03 / RV7-B-CS7 A03 (reproduced) | **NOT ACCEPTED as stated** (RV7-M1). R-2 (b) fails: one onboarding record makes `{onboard}` a minimal set the eight pairs omit. The residual itself (a human must know where the owner publishes) is core. |
| FC-R2′ | An operator who types one source's values for both (`op1src`) | FA7 S2 D (reproduced) | **ACCEPTED** (R-2): inside the root; `gov-admit` shows both sources; RT-184 |
| **FC-R3′** | An operator directed to look-alike sources (`desig1`, `desig2`) | RV7-B-A03 | **NOT ACCEPTED as stated** (RV7-M1): one designation input, not two |
| FC-R5 | Key theft at first contact (CP-FC-KEY-THEFT) | BA12r7 (reproduced); RV7-B-CS7 A01-VB | **ACCEPTED** (R-2) for malicious bytes (G_BYTES). For a **revoked** binary the omission strategy (RV7-H1) adds sets the block does not show: not accepted for G_REVOKED. |
| **CUR-R1** | A revocation issued within the 24 hours before admission (`{win}`, 24 h) | CUR7 W (reproduced); RV7-B-A01 (reproduced); RV7-D-A01 | **NOT ACCEPTED** (RV7-H1). R-2 (b) fails: the bound is the unbounded listing delay plus 24 h (executed: 342 h; also for an admitter revocation and a security-relevant registration). R-2 (a) fails: first-hand listing with a compiled delay bounds it. Reviewer C's ACCEPTED is refuted: C's attacks did not include an omission. |
| RS-2 | A machine without any store, stored codes and a clock set back (`{stored_old, clockback}`) | CUR7 A08; ADM7 CLK (reproduced) | **ACCEPTED** (R-1/R-2): TA-7 on machines without a store; machines with a store fail closed (R-CLK-1) |
| TB-1′ | A malicious binary run directly, outside admission | FA7 S1 (reproduced) | **ACCEPTED** (R-1) |
| AD-2′ | Same-account code before the first admission | ADM7 A07 (reproduced); adm7x X2 (reproduced) | **ACCEPTED WITH CONDITION** CR7-C-1 as strengthened in `11` §6 (RV7-M5): the attack direction holds; the same move-aside discards a legitimate surviving high-water |
| VR-B1′ | Same-account replacement of a user-writable binary | UW6 (retained; B re-run) | **ACCEPTED** (R-1) |
| TB-L4 | Machines without stores lack an accepted-TBM high-water | CUR7 A04 (reproduced) | **ACCEPTED** (R-2) |

## Running machines: anchoring, currency, clock

| ID | Residual | Attacks | Determination |
|---|---|---|---|
| RS-1 | A machine anchored before a revocation that never receives later metadata | BA11r7 (reproduced); RV7-D-A09 | **ACCEPTED** (R-2) for C1–C2 within anchor validity (90 days; CI 7 days), never shown `current`: the owner's core under OP-7 (a), consistent with OWNER-DESIGN-REQUIREMENTS-0002 read with OP-7 (a) (RV7-I3). Its "never C3 without a proof of at most 24 hours" part fails as RS-1b. |
| **RS-1b** | A C3 decision whose proof is a recent anchoring event can be stale by up to 24 hours | RV7-B-A02 (reproduced); cur7x (reproduced) | **NOT ACCEPTED** (RV7-H2). R-2 (b): executed 4.5 months and 882 h. R-2 (c): shown "published as of" now. R-2 (a): a compiled state age at C3 bounds it. |
| RS-1c | A valid pin provisioned before a revocation admits the stale descendant for C1–C2 | BA11r7 `M2-pin*`; RV7-B-A02 CI row | **ACCEPTED** for C1–C2 (R-2). **NOT ACCEPTED** for its C3 statement in `24` §5.2 (RV7-H2; RV7-D-A10 narrows the CI instance to gate-less C3). |
| RS-2b | A restored store, the clock set back into its range, every later statement withheld | BA11r7 CLOCK rows (reproduced); RV7-D-A05 | **ACCEPTED WITH CONDITION** CR7-D-02 (RV7-L9): the 90-day bound holds only if a replayed or persistent `clock_reset` cannot lower the high-water, which no text states |
| RS-3 | A3 deletes or rewrites its own account store | ADM7 (reproduced) | **ACCEPTED WITH CONDITION** CR4-B-01 |
| RS-4 | Pins provisioned by a party the repository writer controls | CS7 CIR `pinprov` | **ACCEPTED** as scoping (TA-9); the scoping does not cover an honest provisioner re-stamping a stored code (RV7-H2) |
| RS-5 | Witness-key compromise (revisions 4–6) | PROF7 EX-01 (reproduced); RV7-B-A08 (reproduced) | **REMOVED BY EXCLUSION** (verified) |
| TG-1, TG-3 | Per-machine decisions; non-trust gates forgeable by A2 | design | **ACCEPTED** |
| TG-2 | Same-user PTY | design | **ACCEPTED WITH CONDITION** CR4-B-01 |

## Binary, registration, reproduction, environment, content

| ID | Residual | Determination |
|---|---|---|
| TB-S1 | Registration custodians at threshold with the reproducer quorum (CP-BYTES) | **ACCEPTED** (R-2): CS7, BA12r7 reproduced; OP-9 (b) + (d) is the owner's selection. Its revocation remedy depends on the RV7-H1 correction. |
| TB-S1 (environment) | Environment reproducers at the quorum | **ACCEPTED** (R-2): ENV7 T1 reproduced with the real `rustc 1.98.1` |
| **TB-S2″** | Both supplier classes, or hidden common provenance (`{env_common}`) | **NOT ACCEPTED as stated** (RV7-M3, RV7-M2). R-2 (b) fails: one supplier class with the other toolchain lineage is a minimal set under the text's reproduction rules (RV7-D-A02: 120 of 144 one-build-per-party assignments); and "independent provenance" is string inequality (RV7-B-A04 reproduced). |
| **TA-12″** | Both toolchain lineages, or the compiler source (`{tc_src}`) | **NOT ACCEPTED as stated** (RV7-M3, RV7-M2). The cross pairs are missing (RV7-D-A02), and two distributions of one lineage count as two (RV7-D-A03). Not relied upon today only because no target is certified. |
| TB-S3 | Common custody of reproducers, environment reproducers or registration custodians | **ACCEPTED** (procedural; RT-180) |
| TB-4, TB-4′ | An insider change accepted by honest verification; two verification processes with pipeline input | **ACCEPTED** (R-2) with CR7-B-06 for OP-8 custody (RV7-I1) |
| AV-S1 | One reproducer key forces a conflict | **ACCEPTED** (R-2): registration revocation remedy (FA7 S5 reproduced) |
| RR-2′ | At a project's first use, the operator confirms an eligible release the repository requests | **ACCEPTED WITH CONDITION** CR7-C-2 (record identity, RV7-M6); the clean-runner case is RV7-M4 (blocking) |
| A8 | Root threshold compromise | **ACCEPTED** (R-1): outside TA-4 |
| CS-1 | Correctness of each classification is a root-ceremony review responsibility | **ACCEPTED WITH CONDITION** CR4-B-05 and CR7-D-04 (RV7-L11: a wildcard `informational` subtree accepts new authority-bearing keys) |
| CS-2 | One registration ceremony per release fixes source, inputs, environments, content and final | **ACCEPTED** (CON6 retained; B re-run) |

## Legacy containment, transactions, recovery

| ID | Residual | Determination |
|---|---|---|
| LR-1 | Legacy binaries on a pre-migration working copy | **ACCEPTED** (`gitops7`, `txn7` reproduced; `matrix7` reproduced: `01-REPRODUCTION.md`) |
| LR-2 | Occupation removed or pre-migration paths restored | **ACCEPTED** (every removal, restore, sparse or dotfile-less copy is `PARTIAL(occupation)` or `LEGACY` under every reading; `gitops7`, `matrix7` reproduced) |
| LR-3 | Explicit operator output paths; nested legacy install | **ACCEPTED** (`matrix7` P-VEND reproduced) |
| LR-4 | A fresh clone or a machine without a per-project record accepts the repository overlay | **ACCEPTED WITH CONDITION** CR7-C-2 and CR4-B-04 (a relocated checkout also degrades to LR-4, RV7-M6) |
| Layout durability | clone, checkout, pull, stash, clean, sparse, archives, line endings, case | **ACCEPTED** (`gitops7` reproduced: 45 operations, every state and tamper flag equal) |
| Crash in the first-install migration (`18` §10, `26` §7) | recovery rolls back or forward, never `ABSENT` or `PARTIAL` | **ACCEPTED WITH CONDITION** CR7-C-3, CR7-C-4, CR7-C-5 (RV7-M7, M8, M9) |
| `20` §6 uninstall result | "leaves `ABSENT`" | **ACCEPTED WITH CONDITION** CR7-C-6 (RV7-L6) |
| C-2 cross-device transaction area | refusal before any write | **ACCEPTED WITH CONDITION** (RT-123, specification only) |
| C-4 entry types; `st_nlink` at use | use-time guard | **ACCEPTED WITH CONDITION** (RT-125, specification only) |
| RA-1 (review r6) | Registration authority at threshold with verification compromises; per-project listing | **ACCEPTED WITH CONDITION** RT-198 (RV7-L12) |

## Owner trade-offs (not residuals)

- **OT-1** and **OT-2** are resolved by OWNER-DESIGN-REQUIREMENTS-0002 (binding). They are no longer open trade-offs. `21` §2 and
  `35` §6 still present them as undecided with options; that text predates -0002 and is restated in `11` CD7-3 (2).

## Summary

| Determination | Residuals |
|---|---|
| **NOT ACCEPTED** | FC-R1′/AD-1″ and FC-R3′ as stated (RV7-M1); CUR-R1 (RV7-H1); FC-R5 for G_REVOKED (RV7-H1); RS-1b and the C3 part of RS-1c (RV7-H2); TB-S2″ and TA-12″ as stated (RV7-M2, RV7-M3) |
| ACCEPTED WITH CONDITION | AD-2′ (CR7-C-1); RS-2b (CR7-D-02); RS-3, TG-2 (CR4-B-01); RR-2′, LR-4 (CR7-C-2); CS-1 (CR4-B-05, CR7-D-04); crash recovery (CR7-C-3…5); uninstall (CR7-C-6); C-2, C-4; RA-1 (RT-198) |
| ACCEPTED | FC-R2′, FC-R5 (G_BYTES), RS-1 (C1–C2), RS-1c (C1–C2), RS-2, RS-4 (scoping), TB-1′, VR-B1′, TB-L4, TG-1, TG-3, TB-S1, TB-S1 (environment), TB-S3, TB-4, TB-4′, AV-S1, A8, CS-2, LR-1, LR-2, LR-3, layout durability |
| REMOVED BY EXCLUSION | RS-5 |
