# Output 21 — Owner options OP-1 … OP-7 (revision 4 analysis)

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved.**
> This page asks the owner for nothing yet, and no option is decided here. For each option it records:
> - the choices and their consequences, computed from the revision-4 rules;
> - whether the choice is security-material;
> - where the answer will be encoded;
> - a **proposal**, labelled as such, where one is stated.
>
> Revision 4 closes blocking class **BC-4** (review r3 CD3-4). The review found the OP-2, OP-4 and OP-7 consequence
> statements of revision 3 materially incorrect. Each is restated from the corrected rules of `23`, `24` and `25`, and the
> evidence is named.

## Summary

| Option | Revision 3 proposal | Revision 4 proposal (not a decision) | Changed in revision 4 | Security-material? | Encoded in |
|---|---|---|---|---|---|
| OP-1 Root keys, threshold, custodians | 3 keys, threshold 2 | same; the ceremony also registers exact precedence, the Overlay Surface, owner-domain slots and, under OP-2 (S1), production sources | ceremony scope | **yes** | root v1; TPS |
| OP-2 Custody per purpose | eleven purposes; `release-final` threshold 1; `release-artifact` (i) | **twelve purposes** (adds `freshness-witness`). **Binary source authority: (S1) root-registered production sources.** `release-final` threshold 1 with standby; `release-artifact` (i); `verification-attestation` threshold 1 | **restated** (binary blast radius from CD3-3; new source-authority choice; witness custody) | **yes** | root grants and thresholds; TPS `eligibility.production_sources` |
| OP-3 Gating | mode A | mode A | **restated** (decision-pin integrity; in-gate state confirmation) | **yes** | TPS `gating` |
| OP-4 Separate candidate key | yes | yes | **restated** (what "no" costs after CD3-3) | **yes** | root grants |
| OP-5 Metadata-age warning | 180 days, informational | 180 days, informational; also shown with `CURRENCY_UNPROVEN` | display | no | binary default |
| OP-6 Trust-root confirmation | confirm once per VTS | confirm once per VTS, with state anchoring | unchanged | **yes** | TPS `bootstrap.op6_mode` |
| OP-7 Currency for machines without a current proof | (a) | **(a), `pin_max_validity_days` 30, `c3_currency_window_hours` 168; witness threshold 2 if (c)** | **restated** (inclusion anchors; pin-currency parameter; witness authority; (d) scope) | **yes** | TPS `bootstrap` |

## OP-1 — Root role

- **Options.** Key count and threshold (3 keys, threshold 2 recommended); custodian independence; hardware and locations.
- **What the root threshold signs in revision 4.** Every Trust Policy. That includes:
  - the Constitutional Surface, with exact precedence registration and presence (`23` §3.5, §4.1);
  - the Overlay Surface directions and migration-writable targets (`23` §11);
  - owner constitutional domain slots (`23` §7.2);
  - historical releases;
  - bootstrap parameters, including the pin-currency parameters and `clock_reset`;
  - the cumulative `lowering_history`;
  - under OP-2 (S1), production sources.
- **Frequency.** Expect one root ceremony per final release that changes the kernel. Under OP-2 (S1), also one per release
  that ships binaries; it is normally the same ceremony.
- **The owner must know:**
  1. The property protected is custodian and device independence.
  2. Losing two keys means a new lineage and reconfirmation everywhere.
  3. Moving any of the above to a non-root key set would let a lower threshold register weaker constitutional content or
     choose production source. That is the rejection class, so it would be an architecture change.
- **Security-material:** yes.

## OP-2 — Signing custody per purpose (restated)

### Purposes and custody

| Purpose | Choices | Proposal |
|---|---|---|
| `release-final` | threshold 1 with equal-custody standby, or threshold 2 | threshold 1 with standby |
| `release-candidate` | own key (OP-4) or shared with `release-final` | own key |
| `release-artifact` | (i) 2 keys, threshold 2; (ii) 3 keys, threshold 2; (iii) (i) plus a root co-signature per production binary, where root custodians run `verify-artifact --stage custodian` **and** compare the attested source with the owner's verification record | (i) |
| `build-attestation` | 1 independent rebuilder, or 2 (threshold 2) | 1 rebuilder, independent of the release signers (KS-10) |
| `verification-attestation` | threshold 1 (one independent verifier), or threshold 2 (two) | threshold 1 |
| `certification-status` | owner token distinct from `release-final` | as revision 3 |
| `revocation` | may share with `certification-status` or `trust-state` | shared with `certification-status` |
| `trust-state` | offline owner key | offline owner key |
| **`freshness-witness`** (only if OP-7 (c)) | keys and threshold; the C3 use needs ≥ 2 keys (compiled minimum). Threshold 1 admits C1–C2 only. Scheduled-signing custody, disjoint from every other purpose (KS-11). | not applicable under the proposed OP-7 (a) |
| `retrieval-profile` | may share with `release-final` | shared |

### Binary source authority (new choice)

| Choice | What decides a production binary's source | Minimum capability set for an accepted malicious binary (`25` §7; `evidence/VA4-verify-artifact-source-scenarios.json`) | Cost |
|---|---|---|---|
| **(S0) attested source only** (architecture minimum) | an ACCEPTED verification attestation of the candidate, referenced by the effective TSS; V8 source equality | route S: `verification-attestation` + `release-candidate` + `release-final` + control of the build input (**3 keys**; **2 keys** under OP-4 "no"). Route B: `release-artifact` ×2 + `build-attestation` + `trust-state` (**4 keys over 3 purposes**) | none beyond existing statements |
| **(S1) root-registered production sources** | S0, and the source must be listed in the effective TPS `eligibility.production_sources[]` | route S needs the **root threshold**; the minimum becomes route B (**4 keys over 3 purposes**) | a root-signed TPS entry per release that ships binaries, normally merged with the kernel registration ceremony |
| **(S2) S0 plus verification-attestation threshold 2** | two independent verifiers attest the source | route S: **4 keys** (3 under OP-4 "no") + pipeline input; route B unchanged | a second verification operator |
| **(S3) S0 plus `CERTIFIED_AS_OF` required for binaries** | the certification key must also sign | route S: **4 keys** (3 under OP-4 "no") + pipeline input; route B unchanged | certification before a binary is announced |

**Proposal (labelled, not a decision): (S1).** It removes both release keys and the verification key from the choice of
TCB source. That is the same authority that already registers constitutional content. The cost is ceremony timing.

**Why the release-final threshold matters.**
- Under (S0), (S2) and (S3), `release-final` is one of route S's keys, so threshold 2 adds one key to route S.
- Under (S1) it does not affect binary acceptance.
- It also bounds forged finals (next section).

**The owner must know (corrected statements):**
1. **One `release-final` key** forges authentic finals. It **cannot choose a binary's source**: V8 source equality refuses
   (`RELEASE_IDENTITY_MISMATCH(source)`, RV3-B-A08 flips). A forged final becomes a policy root only if all of these
   hold:
   - its whole surface is registered in a root-signed TPS (E7);
   - its precedence equals the registration;
   - it passes a local trust gate at ingress.

   Within that registration it sets the kernel value of **52 `project_tunable` and 32 `release_bound` leaves**; the
   project layer can already set the tunables. Revision 3's "only root-registered content becomes a policy root" was
   inexact (RV3-L2). Keys read by security decision points are reclassified so they cannot be tunable (`23` §5.2).
2. **An accepted malicious production binary** needs, at minimum, the capability set of the chosen row above. Revision 3's
   "four keys over three purposes" was false (RV3-B-A08). It is true only for route B, or under (S1).
3. The whitelist forbids `trust-state` with certification or attestation, `release-artifact` with anything, and
   `freshness-witness` with anything (`05` §3).
4. A registered standby key needs the same custody as the active key.
5. The verifier in this programme is an AI session run by the owner. The independence of verification and rebuilding
   comes from the process record, not the key; route I (`25` TB-4) is procedural.

**Security-material:** yes.

## OP-3 — Gating for adoption, update and rollback (restated)

| Mode | Behaviour | Uses the local clock? |
|---|---|---|
| **A `always_gate`** | Every production `init`, `adopt migrate --batch 0`, `update --apply`, rollback and downgrade requires a trust gate confirmed locally (`27`): an interactive terminal with a typed digest prefix and **typed state fingerprint**, or a protected, expiring operator decision pin plus a currency proof. | only for decision-pin expiry and the C3 currency window |
| B `fresh_certified_may_skip_update_gate` | as A, but `update --apply` may skip the gate when the view is `CERTIFIED_AS_OF(n) WITH CURRENCY` (`17` §6) and there is no computed weakening, declared breaking change or declared gate | **yes** (TA-7), for currency |

**Restatement from the revision-4 rules (CD3-4; RV3-M2):**
- **What mode A bounds.** Mode A bounds **ingress** against a repository writer, because answers are local.
- **Decision pins.** Decision pins are honoured only when the governed account cannot write them, and only until
  `expires_at`, while their approved state is in the effective chain. `gov`-executed children are confined, so no
  `gov`-run repository or plugin command can create an approval.
- **"Never answerable by any agent path".** It holds for `gov decide` and every `gov`-executed child. An agent with an
  unconfined shell in the same account can drive a pseudo-terminal and write its own VTS (TG-2); it cannot write
  protected pins.
- **What mode A does not bound.** Mode A does **not** bound Git-delivered use. That class is bounded by E7, floors,
  eligibility, inclusion anchors and currency (`24`), and OP-7 decides unanchored use.
- **Common to both modes.** Computed weakenings need the `weakening` gate. Trust gates are never agent-resolvable. Revoked
  and ineligible releases are refused.
- **Sub-parameters:** `refuse_known_rejected` and `refuse_known_withdrawn` (proposal: true); `local_terminal_only[]`
  (proposal: `downgrade`, `policy_lowering`, `adopt_lineage`, `override_kernel_integrity`).

**Proposal:** mode A. **Security-material:** yes.

## OP-4 — Separate candidate signing key (restated)

- **Options.** **Yes:** a dedicated `release-candidate` key. **No:** one key holds both purposes (whitelisted pair).
- **Consequences of "no" after CD3-3 (corrects revision 3's "'no' no longer exposes binaries", RV3-D-A03):**
  - **That key alone** yields authentic finals and candidates with any source. It **cannot** get a binary accepted: no
    ACCEPTED verification attestation names that source (`ARTIFACT_SOURCE_UNVERIFIED`), and a final promoted from a
    genuine candidate with another source fails V8 (`VA4` RV3-D-A03 rows).
  - **That key plus a stolen `verification-attestation` key**, with control of the build input, yields an accepted malicious binary under (S0): **two keys** instead of three. Under (S2) the attacker also needs the second verifier key; under (S3), the certification key.
    malicious binary under (S0), (S2 with one verifier key stolen: no) and (S3 without the certification key: no). Under
    (S0) that is **two keys** instead of three.
  - Under **(S1)**, OP-4 does not affect binary acceptance.
- **What "no" also costs.** A compromise of the most frequently used key yields authentic finals. Those remain bounded by
  E7, exact precedence registration, eligibility and local trust gates.
- **Proposal:** yes. **Security-material:** yes.

## OP-5 — Trust-metadata age warning

- **Proposal:** 180 days, informational only (doctor D032 MEDIUM).
- **Measurement.** Age is measured from the latest anchoring event. The warning is always shown when the machine is
  `UNANCHORED` or `CURRENCY_UNPROVEN`.
- **Security-material:** no, while informational. Enforced limits belong to OP-7.

## OP-6 — First-install trust-root user verification

| Mode | Behaviour | Effect |
|---|---|---|
| **(a) confirm once per VTS** | first sight of a lineage refuses trusted operations until `gov trust confirm-root <id>`, a flag, or a root pin | TA-5 per machine |
| (b) trust on first use, labelled | pinned as `unconfirmed`; doctor D034 MEDIUM | TA-5 does not hold |
| (c) confirm on every `init` | as (a), per project | more friction |

- **Proposal:** (a). **Security-material:** yes.

## OP-7 — Currency for machines without a current proof (restated; CD3-4)

**What the option decides.** What a machine may do for governed read and mutation (C1, C2) when it has no anchor, or has
an anchor but no current proof.

**Architecture minima the option cannot change** (`24` §9):
- inclusion anchors;
- no C3 or binary acceptance without a currency proof;
- mandatory pin validity;
- a separate witness purpose, with ≥ 2 keys for C3;
- pin and decision-pin integrity with confined execution;
- no `current` label.

| Option | Unanchored machine | Anchored machine | Adds | Who can select which state, and for how long (from the revision-4 rules) |
|---|---|---|---|---|
| **(a) anchored only** | C0 | C1–C2 at the anchored chain at any age of a human or retained anchor; pins only within `pin_max_validity_days`; C3 only with a currency proof | TA-9; TA-7 for pins and the C3 window | **A2/A5** select any genuine descendant of a machine's anchor for C1–C2, on machines anchored before a revocation. Duration: while the machine receives no later statement (human anchors; RS-1 core), or at most `pin_max_validity_days` (pins). For C3: staleness of at most `c3_currency_window_hours`, or none with an in-gate proof. A stale CI pin (100 or 400 days) is not an anchor: the runner refuses (RV3-B-A02 flips). A trust-state key cannot bypass an anchor (RV3-B-A12 flips). |
| (b) anchored with maximum age | C0 | as (a), but C2 refused once the latest anchoring event is older than `max_anchor_age_days` | TA-7 | as (a), with every machine's C1–C2 exposure bounded by `max_anchor_age_days`. Needs honest clocks and periodic re-confirmation; restored backups refuse governed mutation until re-anchored. |
| (c) expiring witnesses | C1–C2 with witnesses at the purpose threshold; C3 with ≥ 2 witness keys | as (a), plus witnesses | TA-7; scheduled witness custody (`freshness-witness`) | Anchored machines: as (a). Stateless runners: A2/A5 within `witness_max_validity_hours` of the newest honest witness. **Witness-key compromise:** keys at the C3 threshold let an attacker present any genuine older TSS as latest on witness-reliant machines, for C1–C3, until root rotation; with threshold 1 registered, for C1–C2. A trust-state key alone cannot witness (RV3-B-A06 flips). |
| (d) compiled epoch accepted for use | C1–C2 labelled `FRESHNESS_UNPROVEN`; C3 never | as (a) | none | **A2/A5** select any genuine state at or above the running binary's **compiled TSS**, for C1–C2 on unanchored machines, indefinitely. That exposes every binary whose compiled TSS predates the newest TSS, including a revocation-only TSS with no TPS raise (RV3-L6; `P4r4` `RV3-D-A04_op7_d_scope`). |

**Pin-currency parameters** (TPS `bootstrap`, all changed only through computed reductions):

| Parameter | Proposal |
|---|---|
| `pin_max_validity_days` | 30 |
| `c3_currency_window_hours` | 168 |
| `max_anchor_age_days` (b) | 180 |
| `witness_max_validity_hours` (c) | 168 |
| `freshness_witness_threshold` (c) | 2 |

**Proposal (labelled, not a decision): (a)** with the parameters above. Under (a):
- no stale pin anchors a CI runner, no trust-state key bypasses an anchor, and no binary is accepted on an aged anchor;
- the clock is used only for pins and the C3 window;
- the costs are re-provisioning CI pins at least every 30 days, and a fresh confirmation for C3 on long-idle machines.

**Evidence:** `evidence/P4r4-trust-state-model.json`, the machine × OP-7 × adversary matrix of 132 rows:
- 77 refuse revoked R7;
- 42 admit it only on machines anchored before the revocation (the stated core);
- 13 admit it only under (d) on unanchored machines, never C3 (the stated owner residual);
- 0 unstated rows; 0 rows labelled `current`.

**Security-material:** yes.
- (b) and (c) add TA-7 for governed use.
- (c) adds witness custody.
- (d) accepts its residual.

**Where the answer lives:** the root-signed TPS `bootstrap` block, compiled into binaries and named by the TBM. A project
cannot select a weaker option.

## Options that materially change the security architecture

| Question | Options |
|---|---|
| Security-material | OP-1, OP-2 (including the binary source authority), OP-3, OP-4, OP-6 and OP-7. OP-5 is not, while informational. |
| Add a clock assumption beyond pins and the C3 window | OP-3 mode B, OP-7 (b), OP-7 (c) |
| Remove an assumption | OP-6 (b) removes TA-5 |
| Accept a residual the architecture otherwise removes | OP-7 (d) |
| Change the binary blast radius | OP-2 source authority (S0–S3); OP-2 `release-final` threshold (under S0, S2, S3); OP-2 `release-artifact` (iii); OP-4 "no" (under S0, S2, S3) |

No option is approved by this document.
