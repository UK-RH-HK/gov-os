# Output 8 — Owner-Option Review (OP-1 … OP-6)

This review does **not** approve any option on the owner's behalf. For each recommended default it states whether the
option is technically coherent, whether the choice materially changes the security architecture, and what the owner
must know before answering the D-0008 gate.

| Option | Architect's default | Technically coherent? | Security-material? | Issues the owner must see |
|---|---|---|---|---|
| **OP-1** Root role | 3 keys, any 2 sign, three named custodians, offline hardware-backed | **yes** | **yes** (G6, TH-23) | (1) The security property is **independence** of custodians and devices, not the head-count. If fewer than three independent humans exist, three hardware devices in at least two locations with documented access still give 2-of-3 against loss, but not against a single dishonest custodian. (2) Losing any two keys forces a new lineage (re-bootstrap). (3) Root keys never touch an online host; the ceremony record holds public data only. |
| **OP-2** Release custody | 1 active hardware token on an isolated signing host + 1 standby registered, held separately | **yes** | **yes** | (1) A registered standby key can sign immediately; its custody must be **equal**, not merely separate. (2) Threshold 1 means one token or host compromise authenticates arbitrary releases for every consumer not yet on a patched binary, and repository-delivered revocation is strippable (RV-H2). Consider threshold 2 for final (non-candidate) releases: release key + an independent co-signer, which could also be the verifier attestation of RV-M5. (3) The isolated host must reproduce `gov release build` from `git archive` without network access; statement fields must be deterministic (RV-L3). |
| **OP-3** Uncertified/rejected adoption | `init`: allowed + labelled; `update`: gate bound to digest; `REJECTED`: gate; `REVOKED`: refused | **only after CD-2** | **yes** | (1) As specified, “REJECTED ⇒ gate” depends on the REJECTED certification statement being **present**. A source controller can omit it, turning a rejected release into `AUTHENTICATED_UNCERTIFIED`, which `init` allows ungated. A stale CERTIFIED can also be replayed without the later WITHDRAWN (RV-H2). (2) `minimum_trust_level` is read from the kernel being evaluated; legacy kernels have no such key (RV-H1). Restate OP-3 in terms of **fresh positive evidence**, with the minimum as a T0 constant that projects may only raise. |
| **OP-4** Separate candidate key | no | **yes**, conditionally | **yes** | Without a candidate marker, every signed candidate becomes a permanently valid, production-installable release unless revoked; this programme produced four rejected candidates in two days. “No separate key” is acceptable only with one of: (a) a signed `release.stage: candidate \| final` field, with production `init`/`update` of `candidate` requiring an explicit flag and gate; (b) mandatory `refuse_install` revocation of every rejected candidate; or (c) a candidate role accepted only by verifier tooling. Option (a) needs no new key. |
| **OP-5** Revocation-freshness warning | 180 days, informational (doctor MEDIUM); overlay may make it gating | **yes** as informational | **no** as informational; **yes** if gating | Making it gating contradicts `07` §2 (“no security decision uses a signer-supplied time”). It would compare a local clock (A3/A4) with a signer's `issued_at`. If a gating freshness rule is wanted, base it on a **sequence** gap against the binary's compiled floor, not wall-clock age. |
| **OP-6** Mandatory `--confirm-trust-root` on first init | no in automation; fingerprint always printed | **yes** (trust on first use) | **yes** | With this default, threat-model assumption TA-5 (a human compares the fingerprint) does not hold for automated installs; the root of trust becomes “whichever binary was obtained” (RV-M6). A coherent middle ground: confirm **once per user trust store or CI environment** (a pinned lineage id that can only narrow trust), plus mandatory fail-closed `TRUST_ROOT_LINEAGE_MISMATCH` when a binary of another lineage opens an existing project. The pack does not yet specify the latter. |

## Options that materially affect the security architecture

OP-1, OP-2, OP-3, OP-4 and OP-6 are security-material. OP-5 is not, provided it stays informational.

OP-3 and OP-4 cannot be answered safely until the correction delta (CD-1, CD-2) is applied: their recommended defaults
rest on certification states that can currently be omitted or replayed.

The pack's statement that “none of them changes the architecture” (`00` §5) should be withdrawn. OP-4 and OP-6 each
change the set of states a production binary accepts.
