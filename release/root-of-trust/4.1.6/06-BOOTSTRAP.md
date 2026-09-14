# Output 6 — Bootstrap model

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 4 makes these changes:
> - binaries are built from **attested source**, and custodians check it (V8, `25` §5.1);
> - state pins carry mandatory validity and live in the system pin directory or under the integrity predicate
>   (`24` §3.2, §3.5);
> - C3 steps need a currency proof; the in-gate typed fingerprint needs no clock (`24` §4.4);
> - the test lineage covers twelve purposes.

## 1. The problem

Every downloaded artefact can be replaced together with anything that claims to authenticate it. Trust enters once, by
comparison with values published **independently of the download channel**, and is carried forward by signatures.

Two such values exist:
- the **trust-root id** (lineage);
- the **state fingerprint** of the currently published Trust State (`24` §3.1).

The remaining loop is *source tree → binary*. It is closed by independent reproduction (`build-attestation`), not by the
release signer.

## 2. Production bootstrap

1. **Root ceremony** (once per lineage). Generate root keys offline; sign root v1 with grants satisfying the compiled
   whitelist (`05` §3); compute the trust-root id and key ids.
2. **Publish fingerprints in at least two channels that do not share an attacker with the release host.** The release
   host is the Git hosting account and anything it serves.
   - Qualifying channels:
     - (a) an offline ceremony record;
     - (b) owner-controlled infrastructure that neither is the Git host nor deploys from it;
     - (c) direct authenticated communication.
   - What is published: the root fingerprint once per lineage, and the **state fingerprint of every new TSS**.
   - Repository copies (`trust/production/fingerprints.txt`, D-0008 appendix) are convenience copies and do not count.
3. **Constitution.** `gov trust draft-policy` produces the next Trust Policy draft: Constitutional Surface, floors,
   eligibility including historical releases, bootstrap block, lowering history. The root ceremony reviews the change list
   and signs (`23` §6.2).
4. **Release.** Reproducible payload build with `release.source` → surface checker exit 0 against the named TPS →
   `release-candidate` signature → independent verification reproducing the candidate from its source →
   `verification-attestation` v2 naming the source → promotion (`release-final`, V8 source equality) →
   `certification-status`.
5. **Binaries.**
   - Built reproducibly from the attested source (`release.source`). Each compiles a Trust Base Manifest v2 (`25` §4) naming its root chain, TPS, TSS, embedded release statement and `binary.source`.
     and embedded release statement.
   - An independent rebuilder checks the attested source (`verify-artifact --stage rebuilder`), reproduces each binary and its TBM digest, and signs a `build-attestation` v2 naming the source.
   - Two `release-artifact` custodians check A1–A4b (`--stage custodian`) and sign `artifact-final.v2`.
   - The next TSS references the artefact statement (`artifacts[]`), and its state fingerprint is published (step 2).
   - A binary cannot embed its own acceptance: the artefact statement, build attestation and TSS ship beside it.
6. **Verifying the first binary on a machine.** Any one of:
   - (a) with an already trusted `gov`: `gov trust verify-artifact` (`25` §5);
   - (b) with independent tooling: verify A2–A6 of `25` §5, including the attested-source binding A4b, with public keys from root metadata whose id was compared with
     a step-2 channel. This means the OpenSSL signature checks of the artefact statement and build attestation, the TSS
     reference, and the TBM digests against the published statements; the release protocol documents the command
     sequence;
   - (c) build from source at the final tag, and compare `gov version --trust` (lineage id and TBM digest) with the
     channel and the build attestation.
7. **Subsequent binaries** are accepted only by `gov trust verify-artifact` (`25` §5, A1–A10). A genuine older binary is
   `BINARY_T0_ROLLBACK` at verification and refuses trusted operations on first run.

## 3. First-install ceremony on a machine (OP-6 and OP-7)

| Step | Command | Establishes |
|---|---|---|
| 1 | `gov trust confirm-root <trust_root_id>` (typed from the channel) or a root pin | lineage confirmation (TA-5) |
| 2 | `gov trust confirm-state <state fingerprint>` (typed from the channel), or a protected state pin with `valid_until` | anchor, satisfied by inclusion (`24` §3.2, §3.4) |
| 3 | `gov trust refresh --from <bundle>` if the machine is `BELOW_ANCHOR` | knowledge at the anchored epoch |
| 4 | `gov init` / `gov update --apply`, with the local trust gate (`27`) and a currency proof: the typed state fingerprint in the gate (no clock), or steps 1–2 within `c3_currency_window_hours` | installation |

**Automation** uses pin files in the system pin directory (`/etc/gov/`, `/Library/Application Support/gov/`, `%ProgramData%\gov\`), or in the account configuration only where the integrity predicate holds. They are provisioned outside the repository writer's control (TA-9 restated, `24` §3.5):
- `trust-root-pins`;
- `trust-state-pins` (`schemas/trust-state-pin.schema.json`, mandatory `valid_until` ≤ `pin_max_validity_days`);
- `approved-trust-decisions` (`schemas/trust-decision-pin.schema.json`, mandatory `expires_at`).

No environment variable, flag or repository file can confirm a lineage or anchor a state (D-0008 rule 15).

A CI runner image provisions `/etc/gov/trust-state-pins`, owned by root, and runs the job as another user. Pins must be
re-provisioned before `valid_until`; the proposed maximum validity is 30 days (`21` OP-7).

OP-6 modes and OP-7 options are analysed in `21`.

## 4. Lineage pinning and mismatch

- The VTS pins the lineage per machine; the lock records `trust_root.id` per project.
- A binary whose compiled lineage (TBM) differs from the lock or the VTS pin → `TRUST_ROOT_LINEAGE_MISMATCH`. It fails
  closed, with no re-pin.
- Re-rooting after a threshold compromise needs `gov trust adopt-lineage <new id>`, run by a human with the
  `adopt_lineage` trust gate (`27`) per project.
- A fork binary with a substituted `trust/production/` is a different lineage and is refused.

## 5. Consumer repository on a new machine

A clone carries `governance/trust/**` (kernel, release statement, PTR state, root links, FORMAT, lock) and the
occupation entries (`26` §2). A bootstrapped binary authenticates them offline.

The new machine's VTS starts empty:
- it is `UNANCHORED` until step 2 of §3;
- what it may do meanwhile is set by OP-7 (`24` §4.3);
- trust ingress is refused.

## 6. Development builds

- `cargo build` from a canonical checkout compiles that checkout's `trust/production/` data into a TBM marked
  `build: development`.
- `verify-artifact` never accepts such a binary.
- Its embedded kernel is `DEVELOPMENT_UNSIGNED` unless the compiled final statement verifies and matches.
- It can install signed releases, but never produces `CERTIFIED` or production eligibility for unsigned material.

## 7. Test fixtures

`gov-test-profile` compiles the test lineage with all twelve purposes. Unsigned fixtures are accepted there as
`DEVELOPMENT_UNSIGNED`. Shipped binaries report `trust_profile: production` in their TBM.

## 8. Classification summary

| Class | Signed by | Authenticity / stage | Production eligibility | Can be CERTIFIED? | Doctor |
|---|---|---|---|---|---|
| Production final, certified | `release-final` + attestation + certification + TSS | `AUTHENTICATED` / `final` | per `19` §6 (including E7) | yes | clean |
| Production final, uncertified | `release-final` | `AUTHENTICATED` / `final` | per `19` §6 | after verification | MEDIUM |
| Production candidate | `release-candidate` | `AUTHENTICATED` / `candidate` | `ELIGIBLE_EVALUATION` only | no | HIGH |
| Legacy 4.1.2–4.1.5 | listed in TPS `eligibility.historical_releases` (root threshold) | `HISTORICAL_IDENTIFIED` | **never** | no | CRITICAL when installed |
| Development unsigned | nobody | `DEVELOPMENT_UNSIGNED` | never | never | HIGH |
| Test | test keys | `TEST` | test profile only | never | — |
| Production binary | `release-artifact` ×2 + `build-attestation` + attested source + TSS reference | accepted by `verify-artifact` with a currency proof | TBM ≥ accepted-TBM high-water | informational certification binding (required under OP-2 (S3)) | — |
