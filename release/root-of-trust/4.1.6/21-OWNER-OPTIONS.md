# Output 21 — Owner options OP-1 … OP-7 (revision 3 analysis)

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved.**
> This page asks the owner for nothing yet, and no option is decided here. For each option it records:
> - the options and their consequences;
> - whether the choice is security-material;
> - where the answer will be encoded;
> - a **proposal**, labelled as such, where one is stated.
>
> The owner answers only after a fresh independent review accepts revision 3 (review r2 §8).
>
> Revision 3 adds OP-7 and restates OP-2, OP-3 and OP-4 as review r2 §8 requires.

## Summary

| Option | Revision 2 recommended default | Revision 3 proposal (not a decision) | Changed in revision 3 | Security-material? | Encoded in |
|---|---|---|---|---|---|
| OP-1 Root keys, threshold, custodians | 3 keys, threshold 2, root holds `trust-policy` | same; the ceremony also registers the Constitutional Surface | ceremony scope stated | **yes** | root v1; TPS signing |
| OP-2 Custody per purpose | nine purposes; `release-final` threshold 1 | **eleven purposes**; `release-artifact` ≥ 2 (compiled minimum) with optional root co-signature; `build-attestation` by an independent rebuilder | **extended** | **yes** | root grants and thresholds |
| OP-3 Gating | mode A | mode A | **restated** (trust gates are local; Git-delivered use belongs to OP-7) | **yes** | TPS `gating` |
| OP-4 Separate candidate key | yes | yes | **restated** ("no" no longer exposes binaries) | **yes** | root grants |
| OP-5 Metadata-age warning | 180 days, informational | 180 days, informational, measured from the anchor time | measurement point | no | binary default |
| OP-6 Trust-root confirmation | confirm once per VTS | confirm once per VTS, in the same ceremony as state anchoring | ceremony combined with OP-7 | **yes** | TPS `bootstrap.op6_mode` |
| **OP-7 Currency for machines without retained or anchored state** | — | **(a) anchored only** | **new** | **yes** | TPS `bootstrap.op7_mode`, `max_anchor_age_days`, `witness_max_validity_days` |

## OP-1 — Root role

- **Options.** Key count and threshold (3 of 2 recommended); custodian independence; hardware and locations.
- **What revision 3 adds.** The root threshold also signs every Trust Policy that registers constitutional content:
  - the Constitutional Surface (`23`);
  - historical releases;
  - bootstrap parameters;
  - lowering history.

  Every final release that changes pinned or unregistered constitutional content needs such a TPS (`23` §6.2, CS-2).
  Expect about one root ceremony per final release that changes the kernel.
- **The owner must know:**
  1. The property protected is custodian and device independence.
  2. Losing two keys means a new lineage and reconfirmation everywhere.
  3. Moving surface registration to a non-root key set would let a lower threshold register weaker constitutional
     content. That is the rejection class, so it would be an architecture change.
- **Security-material:** yes.

## OP-2 — Signing custody per purpose (extended)

| Purpose | Options | Proposal |
|---|---|---|
| `release-final` | threshold 1 with equal-custody standby, or threshold 2 | threshold 1 with standby. After E7 and local trust gates, a stolen token forges authentic finals that can become policy roots only with root-registered content; ingress still needs a trust gate. |
| `release-candidate` | own key (OP-4) or shared with `release-final` | own key |
| **`release-artifact`** | (i) 2 keys, threshold 2 (compiled minimum); (ii) 3 keys, threshold 2; (iii) (i) plus a root co-signature on every production binary | (i). (iii) is strongest but touches offline root keys for every binary build. |
| **`build-attestation`** | 1 independent rebuilder, or 2 (threshold 2) | 1 rebuilder, with a toolchain and custodian independent of the release signers (KS-10) |
| `verification-attestation` | verification operator | as revision 2 |
| `certification-status` | owner token distinct from `release-final` | as revision 2 |
| `revocation` | may share with `certification-status` or `trust-state` (whitelist) | shared with `certification-status` |
| `trust-state` | owner offline key; under OP-7 (c) it must sign expiring heartbeats on schedule | offline key; under (c), a dedicated scheduled-signing custody |
| `retrieval-profile` | may share with `release-final` | shared |

**The owner must know:**
1. The compiled whitelist forbids any key from holding `trust-state` together with certification or attestation, and
   forbids `release-artifact` from sharing with anything (`05` §3).
2. An accepted malicious binary needs four keys over three purposes (`25` §7).
3. A registered standby key needs the same custody as the active key.
4. The verifier in this programme is an AI session run by the owner. The independence of verification and rebuilding
   comes from the process record, not the key.

**Security-material:** yes.

## OP-3 — Gating for adoption, update and rollback (restated)

| Mode | Behaviour | Uses local clock? |
|---|---|---|
| **A `always_gate`** | Every production `init`, `adopt migrate --batch 0`, `update --apply`, rollback and downgrade requires a **trust gate confirmed locally** (`27`): an interactive terminal or an operator decision pin, bound to the statement digests. Certification only changes the recommendation. | no |
| B `fresh_certified_may_skip_update_gate` | As A, but `update --apply` may skip the gate when the view is `CERTIFIED_CURRENT` (`17` §13) and there is no computed weakening, declared breaking change or declared gate | **yes** |

**Restatement (review r2 §8):**
- In revision 2, mode A was **not** a bound against a repository writer, because the gate answer was a repository record
  (review `P2`).
- In revision 3, trust-gate answers are local confirmations. Mode A therefore bounds **ingress** against A2
  (`R3_gate_record_from_repository`).
- Mode A still does **not** bound **Git-delivered use**: A2 committing an older genuine release or stripping trust
  metadata involves no ingress. That class is bounded by E7, floors, eligibility and freshness anchoring, and OP-7 decides
  what an unanchored machine may do.
- Common to both modes (not owner-selectable): absent certification gates; revoked and ineligible releases are refused;
  computed weakenings need the `weakening` trust gate; trust gates are never agent-resolvable.
- Sub-parameters: `refuse_known_rejected` and `refuse_known_withdrawn` (proposal: true); `local_terminal_only[]`
  (proposal: `downgrade`, `policy_lowering`, `adopt_lineage`, `override_kernel_integrity`).

**Proposal:** mode A. **Security-material:** yes.

## OP-4 — Separate candidate signing key (restated)

- **Options.**
  - **Yes:** a dedicated `release-candidate` key.
  - **No:** the root grants both candidate and final purposes to one key (whitelisted pair).
- **Restatement (review r2 §8).**
  - Under revision 2, "no" also exposed **binaries**, because `artifact-final` rode `release-final`.
  - Under revision 3 binaries are a separate purpose (`release-artifact`, threshold ≥ 2, KS-9). Answering "no" no longer
    exposes binaries (evidence `A29`).
  - What "no" still costs: compromise of the everyday candidate-signing key yields authentic **finals**. Those finals
    remain bounded by E7 (only root-registered content can be a policy root), by eligibility, and by local trust gates at
    ingress.
- **Proposal:** yes.
- **Security-material:** yes (blast radius of the most frequently used key).

## OP-5 — Trust-metadata age warning

- **Proposal:** 180 days, informational only (doctor D032 MEDIUM).
- **Revision 3 change.** Age is measured from the anchor time (`24` §4.1), not from the VTS's own last acceptance. The
  warning is always shown when the machine is `UNANCHORED` (R2-L1).
- **Security-material:** no, while informational. Enforced age limits belong to OP-7 (b).

## OP-6 — First-install trust-root user verification

| Mode | Behaviour | Effect |
|---|---|---|
| **(a) confirm once per VTS** | first sight of a lineage refuses trusted operations until `gov trust confirm-root <id>`, a flag, or a root pin | TA-5 per machine |
| (b) trust on first use, labelled | pinned as `unconfirmed`; doctor D034 MEDIUM | TA-5 does not hold |
| (c) confirm on every `init` | as (a), per project | more friction |

- **Revision 3.** Root confirmation and state anchoring (OP-7) happen in the same ceremony.
  - Interactively: `gov trust confirm-root <id>` then `gov trust confirm-state <fingerprint>`.
  - For automation: one pin file carrying both.
- **Proposal:** (a).
- **Security-material:** yes.

## OP-7 — Currency for machines without retained or anchored state (new)

**What the option decides.** What a machine may do when no anchor establishes that its trust state is current: first
install, clean CI runner, restored backup, long absence. See `24` §5. It does **not** decide trust ingress: without an
anchor, trust ingress is always refused (architecture minimum).

| Option | Unanchored machine | Anchored machine | Adds trust assumption | Consequences |
|---|---|---|---|---|
| **(a) Anchored only** | diagnostics only (C0) | everything; anchor age shown, never limited | TA-9 for pins | The review's P4-B5 class is impossible everywhere. Every CI runner needs a state pin outside the repository writer's control. Long-absent machines operate at their anchor (safe, labelled, not fresh). |
| (b) Anchored with maximum age | C0 only | C2/C3 refused after `max_anchor_age_days` | **TA-7 (clock)** | Bounds staleness by time. Needs honest clocks and periodic re-confirmation, and restored backups refuse governed mutation until re-anchored. |
| (c) Expiring witness | C0–C3 while an unexpired witness TSS verifies; C0/C1 after | as (a), plus witnesses | **TA-7**; `trust-state` signs heartbeats on schedule | Stateless CI without pins. Staleness bounded by the expiry window. Beyond expiry, offline machines refuse governed mutation. The trust-state key custody must support scheduled signing. |
| (d) Compiled epoch accepted for use | C0–C2, labelled `FRESHNESS_UNPROVEN`; C3 never | as (a) | none | Keeps revision 2's convenience. **Residual:** a repository writer can select older genuine state for governed use on unanchored machines running binaries older than the newest TPS (review P4-B5). |

- **Proposal (labelled, not a decision): (a).** It adds no clock assumption and removes the class instead of bounding it.
  The owner should weigh the operational cost of provisioning pins for CI against (c)'s clock and heartbeat trade-off.
- **Security-material:** yes. (b) and (c) add TA-7; (d) accepts the P4-B5 residual.
- **Where the answer lives:** the root-signed TPS `bootstrap` block, compiled into binaries and named by the TBM. A project
  cannot select a weaker option; an overlay may require a stronger one.

## Options that materially change the security architecture

- **OP-1, OP-2, OP-3, OP-4, OP-6 and OP-7 are security-material.** OP-5 is not, while informational.
- **Options that add a clock assumption:** OP-3 mode B, OP-7 (b) and OP-7 (c).
- **Options that remove an assumption:** OP-6 (b) removes TA-5.
- **Option that accepts a residual the architecture otherwise removes:** OP-7 (d).
- **OP-4 "no"** enlarges the blast radius of the most frequently used key for finals, not for binaries.

No option is approved by this document.
