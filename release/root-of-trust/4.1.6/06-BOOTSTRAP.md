# Output 6 — Bootstrap model

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 6 changes (BC5-1, BC5-2, BC5-3):
> - the value typed at first contact is the **first-contact code** of a first-contact manifest that commits to lineage, state
>   and admitter digests; the operator procedure and the admitter rules are `32`; which sources are consulted is OP-13;
> - build environments are registered and reproduced first-hand (`33`); registration content is derived first-hand by the
>   custodians (`34`);
> - re-admission keeps the verifier trust store (`31` R-ADM-8′).
>
> Revision 5 changes, kept: releases are registered once per release and binaries are reproduced by a first-person quorum
> (`30`); the first binary on every machine, every CI image and every legacy consumer's first RoT-1 binary are admitted by
> the independent executor `gov-admit`, which never executes the candidate and installs the measured bytes (`31`); no trust
> ceremony runs on a binary that has not been admitted (`31` GB-1′, R-CER-1); revision 4's first-binary paths (b) and (c) stay
> withdrawn.

## 1. The problem

Every downloaded artefact can be replaced together with anything that claims to authenticate it. Trust enters once, by values
published independently of the download channel and read by a person now. It is carried forward by signatures and first-hand
establishment.

Revision 5 used two such values, the trust-root id and the state fingerprint, plus an admitter digest compared with a channel.
Review r5 showed that one channel page then selected the lineage, the Trust Policy that set the channel quorum, and the
evaluator (RV5-H1).

Revision 6 publishes **one** value per Trust State: the first-contact code. It commits to a first-contact manifest `{lineage,
state epoch, admitter digests}`. Every first-contact value is therefore covered by one agreement rule over the sources the
owner designated (OP-13). What no mechanism removes, the **first-contact root**, is stated with its computed minimum
(`32` §6).

## 2. Production bootstrap

1. **Root ceremony** (once per lineage). Root keys offline; root v1 with grants that satisfy the whitelist and the Fact
   Threshold Check (`05` §3, including KS-14), the reproducer quorum and the registration authority of OP-2. The ceremony
   record names each first-contact source's custodian and hosting, and under OP-13 (c) the signing service, under (d) the
   media custodian (CR5-B-02).
2. **First-contact sources (OP-13).** For every new Trust State the owner publishes the first-contact manifest (any carrier)
   and its code (in each designated source):
   - under (a) and (b), one or two owner sources that do not share an attacker with the release host;
   - under (c), additionally, platform-signed `gov-admit` packages carrying the compiled lineage and the build's manifest;
   - under (d), provisioning media for designated machines.

   Qualifying owner sources are an offline ceremony record, owner infrastructure that is not the Git host and does not deploy
   from it, and direct authenticated communication. Repository copies are convenience copies. The state fingerprint of every
   Trust State is also published, for in-gate proofs and `confirm-state` on admitted binaries.
3. **Constitution.** `gov trust draft-policy` produces the Trust Policy draft, runs the derivation calculator and the pack checks
   (`29` §5.3, §5.5), and refuses while any security-material owner option is unanswered. The root ceremony reviews and signs.
4. **Release.**
   1. Reproducible payload build with source identity v2 and the input manifest v2, with its environments (`30` §4).
   2. `release-candidate` signature.
   3. Independent verification records `verification-attestation.v4` for exactly the candidate and the kernel the verifier
      reproduced, returned first-hand (OP-8).
   4. Promotion (`release-final`, V8).
   5. Environment reproductions (`33` R-BENV-2).
   6. **Registration** (`30` R-REG-3 (a)–(g)): each custodian checks upstream checksums, the environment reproductions and the
      records, and derives the constitution block from its own kernel build (`34` R-CON-1).
   7. Certification (optional).
5. **Binaries.** Every registered target is built reproducibly by n independent reproducers from the registered source, in
   re-assembled registered environments, with inputs fetched by digest. Each reproducer signs a one-signature reproduction
   and confirms first-hand to the publisher (`30` §7). The publisher applies E7's restrictors before referencing the
   registration, references exactly one quorum-reproduced digest per target in the next Trust State, and publishes the new
   first-contact manifest and code (`30` §8). The admitter is registered and reproduced the same way, and its digests are
   listed in the Trust Policy's `bootstrap.admitter_digests`.
6. **First binary on a machine: independent admission only** (`31` §4, `32`). The operator runs the first-contact procedure
   FC-1…FC-3 with platform tools. `gov-admit` then enforces FC-4…FC-8 and evaluates admission-predicate/1 (`25` §5) over the
   bytes it read, installs from its buffer, and writes the admission record in the verifier trust store. There is no other
   first-binary path.
7. **Subsequent binaries** are accepted by the admitted `gov` running the same predicate, with its anchors and a currency proof
   that names the Trust State publishing the binary (`25` AP-3).

## 3. First-install ceremony on a machine

| Step | Command | Runs on | Establishes |
|---|---|---|---|
| 0 | FC-1: read the first-contact code from each OP-13 source; FC-2: `sha256sum` of the manifest equals the code; FC-3: `sha256sum` of `gov-admit` equals the manifest's entry for the target (under (c) also the platform signature) | the operator's platform tools (`gov trust fc-procedure` prints the steps) | evaluator selection through the agreed code (the first-contact root) |
| 1 | `gov-admit --code <typed> [--code <typed from the second source>] --manifest <fcm> --statements <bundle> --install <dest> <candidate>` | `gov-admit` | TCB admission; lineage confirmation (the code commits to it); a fresh verifier trust store only at first admission (`31` R-ADM-8′) |
| 2 | `gov trust confirm-state <fingerprint>` typed again, or a protected pin, **on a protected installation** (`31` GB-4′) | the **admitted** `gov` | anchor, satisfied by inclusion (`24` §3.2, §3.4) |
| 3 | `gov trust refresh --from <bundle>` if the machine is `BELOW_ANCHOR` | the admitted `gov` | knowledge at the anchored epoch |
| 4 | `gov init` / `gov update --apply`, with the local trust gate (`27`) and a currency proof naming the TSS used | the admitted `gov` | installation |

Before step 1 completes, every RoT-1 `gov` on the machine runs C0 only (`31` GB-1′). On a user-writable installation, steps 2
and 4 are refused. The classes reachable there are `31` §7.1.

**Automation.** Pins and decision pins live in the system pin directory, or in the account configuration only where the
integrity predicate holds; they are provisioned outside the repository writer's control (TA-9, `24` §3.5).

A **CI runner image** runs steps 0 and 1 at image build, with codes provisioned from the OP-13 sources, or the media under
(d). It writes a root-owned store and admission record with `valid_until` ≤ `pin_max_validity_days`, beside a root-owned state
pin naming the same Trust State, and runs jobs as another user. A job running as root, or with passwordless `sudo`, violates
TA-9: pins are ignored and C3 refuses (`31` GB-6). Images are rebuilt before the record or the pin expires.

No environment variable, flag or repository file can confirm a lineage, anchor a state or admit a binary (D-0008 rule 15).

## 4. Lineage pinning and mismatch

Unchanged: the verifier trust store pins the lineage; the lock records `trust_root.id`; a binary whose compiled lineage
differs is `TRUST_ROOT_LINEAGE_MISMATCH`; re-rooting after a threshold compromise needs `gov trust adopt-lineage` by a human
through the `adopt_lineage` trust gate, and first admission of a binary under the new lineage.

## 5. Consumer repository on a new machine

A clone carries `governance/trust/**` and the occupation entries (`26` §2). The trust tree includes kernel, release and
registration statements, state, root links, FORMAT, lock and the `.gitattributes` member. The admitted binary authenticates
them offline.

The new machine's verifier trust store is empty until first admission. It is `UNANCHORED` until step 2; what it may do
meanwhile is OP-7 (`24` §4.3), and trust ingress is refused.

## 6. Development builds

`cargo build` from a checkout compiles that checkout's trust data into a TBM marked `build: development`. Such a binary is
never admitted, never records an accepted TBM, and never produces production eligibility for unregistered material.

## 7. Test fixtures

`gov-test-profile` compiles the test lineage with the purposes of `05` §1, and a test first-contact manifest and code per test
Trust State.

## 8. Classification summary

| Class | Selected by | Authenticity / stage | Production eligibility | Doctor |
|---|---|---|---|---|
| Production final, registered | registration (OP-2) referenced by the effective TSS, content derived first-hand | `AUTHENTICATED` / `final` | per `19` §6 (E7 with the release's registration and AP-5's restrictors) | clean |
| Production final, not registered (or not yet held) | — | `AUTHENTICATED` / `final` | ineligible (`release_unregistered`) | HIGH |
| Production candidate | `release-candidate` | `AUTHENTICATED` / `candidate` | `ELIGIBLE_EVALUATION` only | HIGH |
| Legacy 4.1.2–4.1.5 | TPS `eligibility.historical_releases` (root threshold) | `HISTORICAL_IDENTIFIED` | never | CRITICAL when installed |
| Development unsigned | nobody | `DEVELOPMENT_UNSIGNED` | never | HIGH |
| Production binary | admission-predicate/1: registration + reproduction quorum under registered environments + publication + negatives + currency, by an evaluator other than the candidate; at first contact, the agreed first-contact code | admitted, record written in the store | TBM ≥ accepted-TBM high-water | — |
