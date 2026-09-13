# Output 6 — Bootstrap model

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 2 addresses RV-M6 (CD-10): publication channels independent of the release host, OP-6 restated as a
> first-install user-verification decision, lineage pinning with fail-closed mismatch, and development/fork builds.

## 1. The problem

Every downloaded artefact can be replaced together with anything that claims to authenticate it. The first trusted
`gov` binary therefore cannot be authenticated by bytes that arrive with it. Trust enters once, through a comparison
with a value published **independently of the download channel**, and is carried forward afterwards by signatures.

There is no hidden release→keys→release loop: the root is compiled into the binary from `trust/production/`, releases
never supply it, and bundles can only extend the compiled chain by dual-threshold links (`05` §8). The remaining loop
is *source tree → binary*, which is the trusted computing base (`01` TA-1). Only a human fingerprint comparison breaks
it (TA-5), and OP-6 decides when that comparison happens.

## 2. Production bootstrap

1. **Root ceremony** (once per lineage). Generate root keys offline; sign root version 1 with purpose grants
   (`05` §3); compute the trust-root id (`sha256:` of the canonical v1 payload) and all key ids.
2. **Publish the fingerprint in at least two channels that do not share an attacker with the release host.** The
   release host is the Git hosting account and anything it serves. Qualifying channels:
   - (a) a printed or offline ceremony record held by the root custodians;
   - (b) a publication on infrastructure the owner controls that is not the Git host and does not deploy from it (for
     example the organisation's own domain or internal documentation system);
   - (c) direct communication to consumer operators through an existing authenticated channel (for example signed email
     from a known key, or an in-person handover).

   Copies inside the repository (D-0008 appendix, release protocol on `main`) are convenience copies and **do not
   count** towards the two.
3. **Release.** Reproducible build → unsigned candidate statement → sign-what-you-reproduced (`release-candidate`) →
   independent verification → `verification-attestation` → promotion to final (`release-final`, same content, new
   sequence, `promoted_from_candidate`) → `certification-status` → Trust State publication (`17`).
4. **Binaries** are built from the final tag. Each compiles the root chain, newest TPS, newest TSS with its referenced
   statements, historical-identity registry, and embedded kernel with its final statement. An `artifact-final`
   statement lists each binary's name, target, SHA-256, size and trust profile. Binaries cannot embed their own
   certification: certification follows verification of the built binary, and its TSS ships beside the binary.
5. **Verifying the first binary on a machine** — any one of:
   - (a) with an already trusted `gov`: `gov trust verify-artifact <binary> <artifacts.dsse.json>`;
   - (b) with independent tooling: compute SHA-256 of the binary; reconstruct `PAE(payloadType, payload)` from the
     envelope; verify the Ed25519 signature with a `release-final` public key taken from the root metadata whose
     trust-root id was compared with a step 2 channel. The release protocol documents the OpenSSL 3 command sequence.
   - (c) build from source at the final tag, then compare the trust-root id printed by `gov version --trust` with a
     step 2 channel.
6. **Subsequent binaries** are authenticated by the previous one (5a). They must carry a root chain of the same lineage
   whose version is ≥ the VTS high-water; otherwise `gov trust verify-artifact` reports `TRUST_ROOT_LINEAGE_MISMATCH` or
   `TRUST_ROOT_ROLLBACK`.

## 3. First-install trust-root user verification (OP-6)

OP-6 does not change how releases are authenticated against a pinned root. It decides **whether, and when, a human
confirms that the root compiled into this binary is the published one** before the machine pins it.

| Mode | Behaviour | TA-5 holds? |
|---|---|---|
| **(a) Confirm once per Verifier Trust Store** (recommended) | The first time a lineage is seen by a VTS, trusted operations (ingress, trusted mutations) refuse with `TRUST_ROOT_UNCONFIRMED` until `gov trust confirm-root <trust_root_id>` is run by a human who compared the id with a step 2 channel. Automation supplies the id through an explicit `--confirm-trust-root <id>` flag or a machine pin file at `<account-home>/.config/gov/trust-root-pins` (resolved from the account database, not the environment). A pin can only confirm the lineage it names; a mismatch refuses. | yes, per machine and CI environment |
| (b) Trust on first use, labelled | The lineage is pinned without confirmation, recorded `confirmation: unconfirmed`; doctor D034 MEDIUM on every project using it. | **no**: the root of trust reduces to authenticity of the obtained binary (§2.5) |
| (c) Confirm on every `init` | As (a), but required per project. | yes |

The confirmation record (`{trust_root_id, method: human \| pin \| unconfirmed, at, operator}`) lives in the VTS. The
project lock records the lineage id and the confirmation method seen at install. No environment variable can confirm a
lineage (D-0008 rule 15).

## 4. Lineage pinning and mismatch

- The VTS pins the lineage per machine. The lock records `trust_root.id` per project.
- A binary whose compiled lineage differs from the lock's `trust_root.id` or from the VTS pin → `TRUST_ROOT_LINEAGE_MISMATCH`.
  This fails closed: the installed kernel is not a policy root (E6), mutations are refused, and there is no re-pin.
  Legitimate re-rooting after a threshold compromise (`05` §9) needs an explicit `gov trust adopt-lineage <new id>` run
  by a human, with a Human Decision Gate per project.
- A fork binary built from a canonical checkout with a substituted `trust/production/` is a different lineage and is
  refused by every project and machine pinned to the genuine one.

## 5. Consumer repository on a new machine

A clone carries `governance/kernel/**`, `governance/trust/**` (release statement, PTR state, root links, FORMAT) and
`framework.lock`. A bootstrapped binary authenticates them offline (`18` §6). The new machine's VTS starts empty, so the
lineage is confirmed per OP-6, and the per-project high-water (`20` §9) starts from this install. Nothing is downloaded.

## 6. Development builds

`cargo build` from a canonical checkout compiles that checkout's `trust/production/` root, TPS and TSS. The embedded
kernel is authenticated only if the checkout's compiled final statement verifies and matches the embedded bytes.
Otherwise the embedded kernel is `DEVELOPMENT_UNSIGNED`, and `gov version --trust` reports `build: development`.

A development binary can install signed releases normally. It cannot install its own embedded kernel as authenticated
and can never produce `CERTIFIED` or an eligible state for unsigned material.

## 7. Test fixtures

The separate `gov-test-profile` binary (`05` §10) compiles the test lineage. Certification tests sign fixtures at test
time with committed test keys. Unsigned fixtures (for example `fixtures/update/previous-release/4.1.1`, harness v1's
synthetic `prev-4.1.1`) are accepted there as `DEVELOPMENT_UNSIGNED`. The release pipeline asserts that shipped
binaries report `trust_profile: production`.

## 8. Classification summary

| Class | Signed by | Accepted by | Authenticity / stage | Production eligibility | Can be CERTIFIED? | Doctor |
|---|---|---|---|---|---|---|
| Production final, certified | `release-final` + attestation + certification + TSS | production binaries | `AUTHENTICATED` / `final` | per `19` §6 | yes | clean |
| Production final, uncertified | `release-final` | production | `AUTHENTICATED` / `final` | per `19` §6 | after verification | MEDIUM |
| Production candidate | `release-candidate` | production (evaluation only), verifier tooling | `AUTHENTICATED` / `candidate` | `ELIGIBLE_EVALUATION` only | no (its promoted final can be) | HIGH |
| Legacy 4.1.2–4.1.5 | compiled historical-identity registry (`release-final`) | production (recognition only); test profile | `HISTORICAL_IDENTIFIED` / `historical` | **never** | no | CRITICAL when installed |
| Development unsigned | nobody | production with `--allow-unsigned-development`; test profile | `DEVELOPMENT_UNSIGNED` | never (production) | **never** | HIGH (D030) |
| Test | test keys | `gov-test-profile` only | `TEST` | test profile only | **never** | — |
