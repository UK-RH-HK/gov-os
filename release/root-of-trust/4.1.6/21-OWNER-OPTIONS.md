# Output 21 — Owner options OP-1 … OP-6 (revised analysis)

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved.** This page asks the owner for
> nothing yet. It records, for each option, the revision 2 recommended default, what changed since revision 1, whether
> the choice materially changes the security architecture, and where the answer will be encoded once given.
> Revision 2 withdraws the rev 1 statement that “none of them changes the architecture” (`00` rev 1 §5).

## Summary

| Option | Rev 1 default | Rev 2 recommended default | Changed? | Security-material? | Encoded in |
|---|---|---|---|---|---|
| OP-1 Root keys, threshold, custodians | 3 keys, threshold 2, three custodians | same, plus root also holds `trust-policy`; custodian **independence** made explicit | clarified | **yes** | root v1 (`purposes.root`, `purposes.trust-policy`) |
| OP-2 Signing custody per purpose | release: token + standby | custody matrix for all nine purposes (§2); `release-final` threshold 1 with equal-custody standby, threshold 2 optional | extended | **yes** | root grants and thresholds |
| OP-3 Adoption and update gating | init allowed; update gated unless CERTIFIED; REJECTED gated | **mode A**: every production install, update and rollback requires a Human Decision Gate bound to the statement digest; certification is informational; known REJECTED/WITHDRAWN refused | **restated** | **yes** | TPS `gating` (root-signed) |
| OP-4 Separate candidate key | no | **yes**: separate `release-candidate` purpose key | **reversed** | **yes** (key exposure) | root grants |
| OP-5 Freshness warning | 180 days, informational, overlay may gate | 180 days, **informational only** | narrowed | **no** | binary default + overlay (informational) |
| OP-6 Trust-root confirmation | none mandatory; fingerprint printed | **mode (a)**: confirm once per Verifier Trust Store (human or pin) | **restated** | **yes** | VTS policy, binary default |

## OP-1 — Root role

- **Recommendation:** 3 root keys, threshold 2, offline hardware-backed, geographically separated. The same keys hold
  `trust-policy` (floors, eligibility, install authority, gating) at the root threshold (`05` KS-1, KS-2).
- **What changed:** root now also signs Trust Policy Statements, so every floor raise (`19` §10) needs a root ceremony.
  Floors change rarely; the frequency is expected to be one ceremony per floor-raising release.
- **Security-material:** yes. The root threshold defines lineage takeover resistance (TH-23) and floor-lowering
  resistance (TH-24).
- **The owner must know:**
  1. The property protected is **independence** of custodians and devices, not head-count. With fewer than three
     independent people, three devices in at least two locations still protect against loss, not against one dishonest
     custodian.
  2. Losing two keys means a new lineage and a reconfirmation on every machine (`05` §9).
  3. An owner who wants floor raises without a root ceremony would need a separate `trust-policy` key set. KS-2 forbids
     that in revision 2, because floors are constitutional. Changing it would be an architecture change.

## OP-2 — Signing custody per purpose

| Purpose | Recommended keys / threshold | Custody | Grant sharing permitted |
|---|---|---|---|
| `release-final` | 1 active + 1 standby, threshold 1 (**option: 2**) | hardware token on an isolated signing host; standby with **equal** custody | `retrieval-profile` |
| `release-candidate` | 1, threshold 1 | signing host (lower custody acceptable; candidates are never production-eligible) | — |
| `verification-attestation` | 1, threshold 1 | the verification operator; never a key holding `release-*` or `certification-status` (KS-4…KS-6) | — |
| `certification-status` | 1 + standby, threshold 1 | owner hardware token, distinct from `release-final` (KS-3) | `revocation` |
| `revocation` | 1, threshold 1 | owner | `certification-status`, `trust-state` |
| `trust-state` | 1, threshold 1 | owner, offline | `revocation` |
| `retrieval-profile` | 1, threshold 1 | release owner | `release-final` |

- **Security-material:** yes.
- **The owner must know:**
  1. A registered standby key can sign immediately. It needs the same custody as the active key.
  2. With `release-final` threshold 1, one stolen token forges authentic finals for every verifier that has not
     received the key revocation (`17` RS-1). Two things still apply to such a forgery: every install and update needs a
     human gate (OP-3 mode A), and a CERTIFIED view needs two further keys plus a trust-state reference. Threshold 2
     (release key plus an independent co-signer) removes single-token forgery at the cost of a second custodian per
     release.
  3. Distinct keys do not create distinct people. A single owner can hold several purposes; the constraints only stop one
     stolen key from spanning authenticity and certification.
  4. The verifier in this programme is an AI session run by the owner. The attestation key's holder is therefore the
     owner's delegate. The independence of the verification comes from the process record, not from the key.

## OP-3 — Gating for adoption, update and rollback (restated)

**Why restated.** The independent review showed that the rev 1 default depended on certification statements that a
source controller can omit (REJECTED) or replay stale (CERTIFIED without the later WITHDRAWN). Revision 2 defines gating
in terms of **fresh positive evidence**, and absence of such evidence always gates (`17` MS-1, MS-3).

| Mode | Behaviour | Uses local clock? | Can withholding or replaying certification bypass it? |
|---|---|---|---|
| **A — `always_gate`** (recommended) | Every production `init`, `adopt migrate --batch 0`, `update --apply`, rollback or downgrade requires a Human Decision Gate (for `init`, an acknowledgement recorded as a gate) bound to the statement digest(s). The gate shows authenticity, eligibility, certification view with its sequence, trust-state status and computed weakenings. Certification only changes the recommendation. | no | **no** — certification never removes a gate |
| B — `fresh_certified_may_skip_update_gate` | As A, except `update --apply` may skip the gate when the view is `CERTIFIED_CURRENT` (`17` §13): an unexpired TSS by local clock, no signed reference newer than the TSS, no computed weakening, no declared breaking change or gate. `init` and rollback always gated. | **yes** | only by an attacker who controls the local clock (A3/A4) and holds a genuinely CERTIFIED, unexpired state |

Common to both modes, and not owner-selectable: absence of certification gates; revoked releases are refused; ineligible
releases are refused (`19` §6); computed weakenings are gated (`19` §9).

Sub-parameters (encoded in TPS `gating`):
- `refuse_known_rejected`: recommended **true** — a final whose highest known certification is REJECTED is refused, not
  gated;
- `refuse_known_withdrawn`: recommended **true**.

- **Security-material:** yes. Mode B introduces trust in the local clock for one decision and requires the trust-state
  publisher to issue expiring TSSs on a schedule.
- **Where the answer lives:** in the root-signed Trust Policy, so a project cannot select a weaker mode. The overlay can
  force mode A.

## OP-4 — Separate candidate signing key (reversed)

- **Recommendation:** yes. A dedicated `release-candidate` purpose key signs candidates; `release-final` signs only
  promotions to final.
- **Why reversed:** revision 2 signs `release.stage`, and production eligibility requires `final` (`19` E2). Without a
  separate key, the key used several times a day during repair iterations is the same key that can create
  production-eligible finals. With it, the frequently used key can create only candidates, which are never
  production-eligible and cannot be certified.
- **If the owner answers no:** the root grants both purposes to one key. Stage separation and eligibility still hold
  (signed field, E2). What is lost is exposure separation: compromise of the everyday signing key yields finals.
- **Security-material:** yes (key exposure and blast radius); not for the eligibility logic.

## OP-5 — Trust-metadata age warning (informational only)

- **Recommendation:** after 180 days since this machine last accepted new signed trust metadata, doctor D032 reports
  MEDIUM. Informational only.
- **What changed:** rev 1 allowed an overlay to make this gating. Revision 2 removes that. Gating on wall-clock age would
  compare a local clock (A3/A4) with signer time, contradicting D-0008 rule 7's use of time only in OP-3 mode B.
  Architecturally required staleness is already handled by signed references (`17` S7–S9: `STALE` is gating at ingress,
  not owner-selectable).
- **Security-material:** no, as long as it stays informational.

## OP-6 — First-install trust-root user verification (restated)

- **What the option actually decides:** whether a human confirms, against a channel independent of the release host
  (`06` §2 step 2), that the root compiled into a newly obtained binary is the published one, before the machine pins that
  lineage. It does not affect how releases are authenticated against a pinned root.

| Mode | Behaviour | Threat-model effect |
|---|---|---|
| **(a) confirm once per Verifier Trust Store** (recommended) | First sight of a lineage on a machine or CI environment → trusted operations refused (`TRUST_ROOT_UNCONFIRMED`) until `gov trust confirm-root <id>`, `--confirm-trust-root <id>`, or a pin file from the account configuration | TA-5 holds per machine |
| (b) trust on first use, labelled | pinned as `unconfirmed`; doctor D034 MEDIUM | TA-5 does **not** hold; trust reduces to authenticity of the obtained binary |
| (c) confirm on every `init` | as (a), per project | TA-5 holds; more friction |

- Independent of the mode: lineage mismatch on an existing project fails closed (`06` §4), and no environment variable
  can confirm a lineage.
- **Security-material:** yes. Under (b), a first install from a compromised release host (binary, root and fingerprint
  copies all replaced) is undetectable (`01` TH-37).

## Options that materially change the security architecture

- **OP-1, OP-2, OP-3, OP-4 and OP-6 are security-material.** OP-5 is not while it remains informational.
- **OP-3 mode B** is the only choice that adds a trust assumption (the local clock).
- **OP-6 mode (b)** is the only choice that removes one (TA-5).
- **OP-4 “no”** does not weaken eligibility, but enlarges the impact of the most frequently used key.

None of these options is approved by this document. They are presented for the owner's decision after a fresh
independent review of revision 2.
