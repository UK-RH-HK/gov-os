# 04 — HO-0001 §3–§4 owner requirements and owner options (review r4 synthesis D, AR-0008)

Each requirement is judged as a class: `SATISFIED` only if every sub-item holds under reproduction and held-out attack.

## §3.1 Constitutional-floor closure (R2-H1) — NOT SATISFIED

| Sub-item | Determination | Evidence |
|---|---|---|
| Complete constitutional key inventory | holds | CSI check framework exit 0 (R02) |
| Default-deny handling of unknown new constitutional keys | holds, except the wildcard `informational` rule (RV4-L1) | B U03–U05, U07, U08 exit 2; U01, U02 exit 0 (R08) |
| An explicit floor mode for each mutable field | holds | inventory; lint |
| Coverage check failing the release | holds | exits 0/3/2/2/2 (R02); self-test 56/56 (R01) |
| Schema evolution cannot silently introduce an unfloored setting | **fails** | a higher-sequence release restores superseded registered non-orderable content with no reduction, gate or detector (RV4-H3; R08 part P; D-A02) |
| Test: role→authority map | holds | P1r4 (R05) |
| Test: sensitivity and indexing exclusions | **fails** under retention | secret-pattern rollback executed on 4.1.5 (R08 part P) |
| Test: irreversible Human Gate authority | holds | P1r4 ceiling (R05) |
| Test: plugin and tool permission floor | **fails** under retention | tool descriptor member T1 (D-A02) |
| Test: outbound and export controls | holds | P1r4 shrink_only (R05) |
| Test: project override controls | holds | P1r4 A1, B (R05); lattice (R14) |
| Test: install and update authority | holds | P1r4 floor (R05) |
| Test: exception authority | holds | self-test S16, S55 (R01) |
| Test: future unknown constitutional field | holds | B U07; review-r3 D-A09 re-run (R15) |

## §3.2 New-machine trust bootstrap (R2-H2) — NOT SATISFIED

| Sub-item | Trust state | First TCB | Evidence |
|---|---|---|---|
| First install | holds (inclusion anchor; C3 needs a proof) | **fails**: path (b) accepts a revoked or remediated binary; path (c) self-report; ceremonies on the unaccepted binary | R06 `FB`; R07 AF3; R09 part B; D-A04 |
| Clean CI runner | holds (pins expire; writable pins ignored) | **fails** for the image's first binary (same procedures); RS-2 not as stated | R06 LB3; RV4-M4 |
| Machine restored from backup | holds | n/a (binary already accepted) | P4r4 M3 (R03) |
| Old trust epoch | holds | n/a | P4r4 M4 |
| No trust epoch | holds | as first install | P4r4 M5 |
| Two machines at different epochs | holds | n/a | P4r4 M6 |
| Offline after long absence | holds | n/a | P4r4 M7 |
| Safety vs freshness distinguished; what is gated; monotonic state; OP-7 effects | holds, except RS-2 (RV4-M4) and the witness input under (c) (RV4-M3) | — | `24` §2, §4, §8, §9; R06 |
| Signed-state replay | holds | — | P4r4 R1, R2 |
| Gate records from repository state | holds | — | r2 P2 legacy behaviour (R13); P4r4 R3 |
| OP-7 not decided | holds | — | D-0008 has no `chosen_option` |

## §3.3 Binary and root authenticity (R2-H3) — NOT SATISFIED

| Evaluated item | Determination | Evidence |
|---|---|---|
| A single lower-threshold release key cannot mint a malicious binary | **fails**: one `build-attestation` or `verification-attestation` key plus pipeline input | RV4-H1; R06 `BC`; R07 AF1, AF2; D-A07 |
| Trust chain non-circular | **fails** for the first binary on a machine and for Phase 4 | RV4-H2 |
| Protected: compiled trust roots, floors, trust-policy identity, historical set, trust-state and bootstrap rules | holds for binaries accepted by `verify-artifact` (A6, A7) | R03, R04 |
| Threshold root signature, separate attestation, certification binding, reproducible-build evidence, TBM digests, multi-signature | evaluated in `25` §2; the adopted combination fails the first sub-item | `25` §2, §7 |

## §3.4 Legacy-binary damage containment (R2-H4) — SATISFIED

| Protected path class | Root-anchored (`--root`) invocations | Subdirectory-rooted invocations | Evidence |
|---|---|---|---|
| Kernel paths | no write | a nested-root CIT or `init` inside `governance/trust/kernel/` changes the installed kernel → `KERNEL_TAMPERED` (fail closed) | R20; D-A01 N2, N3 |
| Legacy lock paths | no write | nested installs write their own lock; the occupation lock directory is untouched | R20 |
| Trust paths | no write | litter under `governance/trust/` changes no statement or lock; deleting `governance/trust/framework.lock` → `PARTIAL` | R17; D-A01 N1, N2 |
| Rollback, reinstall, init-force, migration paths | no write | act on the nested install only | R20 |
| Defence independent of old binaries understanding RoT-1 | holds | holds | occupation by type |
| No silent mutation of kernel or trust state into a state treated as valid | holds | holds; overlay rewrites are `COMPLETE` but detected where recorded and LR-4 elsewhere | D-A01 N1b |

Carried: RV4-M1 (closed trust entry sets, root discovery, restated LP-1 and rules, subdirectory test positions), RV4-M6.

## §4 Forward-compatibility constraint — SATISFIED for classification

| Item | Determination | Evidence |
|---|---|---|
| New constitutional file classified with inventory data, default deny | holds | B U07, U08; review-r3 D-A09 re-run (R15); architect's release-consistent re-run |
| Capability Acceptance Contract (owner-supplied) | classified by owner-domain slots; set binding missing (RV4-L10) | D-A08 |
| Gate W policy, G0–G6 scheduler keys | classified; units of work under VU-11 | `23` §7.1; `18` §6.3 |
| New files using `pinned`, member or `pinned_file` shapes | inherit RV4-H3 until registrations are release-scoped | D-A02 |

## Owner options

### Pre-decided?

No. `21` labels every proposal; D-0008 has `in_effect: false` and no `chosen_option`; OP-1 … OP-7 are pending.

### Consequence statements

| Option | Statement in `21` (or `05`) | Determination | Evidence |
|---|---|---|---|
| OP-1 | root threshold scope | accurate | — |
| OP-2 source authority (S0)–(S3) | minimum capability sets | **false** | RV4-H1 |
| OP-2 `release-artifact` (iii) | root co-signature per binary with source comparison | **overstated**: does not stop malicious bytes for genuine source | D-A07 |
| OP-2 rebuilder count | offered; consequence absent | **incomplete** | RV4-H1 |
| OP-2 (S1) cost | one TPS entry per release | **incomplete** | RV4-L9 |
| OP-2 item 1 / `05` §1 `release-final` blast radius | 52 tunable + 32 release-bound leaves; gate at ingress | **false** | RV4-H3; RV4-L8 |
| OP-3 mode A | "never answerable by any agent path" | holds for direct writes only | RV4-M2 |
| OP-4 | consequences of "no" | **garbled; counts inherit RV4-H1** | RV4-L7 |
| OP-5 | informational | accurate | — |
| OP-6 | (a)/(b)/(c) and TA-5 | **incomplete**: TA-5 depends on first-binary acceptance | D-A04 |
| OP-7 (a) | RS-2 bound under (a) | **false** | RV4-M4 |
| OP-7 (b), (d) | exposures | accurate (B's sweep reproduced) | R06 |
| OP-7 (c) | bound relative to the newest honest witness | exact only with independent witness input | RV4-M3 |

### Answer sets that change security (combinations)

| Combination | Security consequence under revision 4 as written |
|---|---|
| (S1) + OP-4 yes + one rebuilder + `release-artifact` (i) (the proposal) | malicious bytes: {ba, pipeline}; malicious source: root threshold |
| (S0) + OP-4 no + one verifier | malicious bytes: {ba, pipeline}; malicious source: {va, pipeline} (REJECTED verdict not held) |
| any + `release-artifact` (iii) | as without (iii) for malicious bytes of genuine source |
| any + two rebuilders | malicious bytes: {ba, ba2, pipeline} |
| OP-6 (b) | TA-5 does not hold; lineage protection then rests entirely on the binary's compiled lineage, which RV4-H2 leaves unanchored on first install |
| OP-6 (a) or (c) on first install | confirmations run on the unaccepted binary (D-A04) |
| OP-7 (a) + stateless pinned runners + clock or time-source adversary | expired pins valid; P1 proof current; C3 and `verify-artifact` on revoked state (RV4-M4) |
| OP-7 (c) + witness service polling the Git host | stale state witnessed without key compromise (RV4-M3) |
| OP-3 decision pins + owner-domain slots | superseded contract members approvable indefinitely (RV4-L5, RV4-L10) |

### Complete?

No. No option makes the faithful-build fact depend on the `release-artifact` or root threshold, and no option or rule gives
anchored first-binary acceptance.

## Inputs the owner decision package will need (after a revision is accepted)

Not produced here, because the verdict is `REJECTED`. The package will need the corrected minimum capability sets per
answer set (CD4-1), the first-binary procedure's assumptions (CD4-2), the release-scoped registration cost (CD4-3), and
the restated OP-6 and OP-7 consequences (CD4-4).
