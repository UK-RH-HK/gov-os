# Output 6 — Bootstrap model

## 1. The problem

Every downloaded artefact can be replaced together with anything that claims to authenticate it. The first trusted
`gov` binary therefore cannot be authenticated by bytes that arrive with it; trust must enter once, through a human
comparison with a value published independently of the download channel, and thereafter be carried forward by
signatures.

## 2. Production bootstrap

1. **Root ceremony** (once per trust lineage): generate root keys offline; sign trust-root version 1; compute the
   trust-root id (`sha256:` of the canonical v1 payload) and the key ids. Publish the fingerprint in at least two
   channels that do not share an attacker with the release host: (a) the owner-approved decision record for D-0008
   (appendix added after the ceremony), (b) the release/distribution protocol on `main`, and (c) one channel outside the
   repository host (e.g. the organisation's internal documentation or a printed ceremony record kept by custodians).
2. **Release**: reproducible build → unsigned statement → sign-what-you-reproduced → signed `release.dsse.json`
   committed under `release/releases/<v>/` → tag.
3. **Binaries**: built from the tag, embedding the trust-root chain, revocation floor, kernel bytes and the signed
   statement. An **artifact statement** (release role) lists each binary's name, target, SHA-256 and size. Binaries cannot
   embed their own certification (certification follows verification of the built binary); certification statements ship
   beside them and inside consumer `governance/trust/`.
4. **First binary on a machine** — the operator obtains the binary and `artifacts.dsse.json` through any transport
   (e.g. a private GitHub release) and verifies it by **one** of:
   - (a) an already trusted `gov`: `gov trust verify-artifact <binary> <artifacts.dsse.json>`;
   - (b) independent tooling: compute SHA-256 of the binary, reconstruct `PAE(payloadType, payload)` from the envelope,
     and verify the Ed25519 signature with the published release public key using a standard tool (the release protocol
     amendment documents the exact OpenSSL 3 command sequence), confirming the release key is listed in the trust-root
     metadata whose fingerprint was published out of band;
   - (c) build from source at the release tag after verifying the tag's signature, then compare fingerprints.
5. **Fingerprint confirmation**: `gov version --trust` prints `trust_profile`, `trust_root_id`, `root_version`, role key
   ids and the embedded kernel trust level. The operator compares `trust_root_id` with the published value. `gov init`
   always prints it in human output and records it in `framework.lock`; OP-6 decides whether `--confirm-trust-root <id>`
   is mandatory.
6. **Subsequent binaries** are authenticated by the previous one (4a) and must carry a root chain whose lineage equals the
   recorded `trust_root_id` and whose version is ≥ the recorded high-water mark; `gov trust verify-artifact` reports a
   lineage change as `TRUST_ROOT_INVALID`.

## 3. Consumer repository on a new machine

A clone carries `governance/kernel/**`, `governance/trust/*.dsse.json` and `framework.lock`. A bootstrapped binary
authenticates them offline (kernel_trust v2). Nothing is downloaded; GitHub availability is irrelevant.

## 4. Development build

`cargo build` from a canonical checkout compiles the public trust root from `trust/production/` — trusting that file is
the same as trusting the source code being compiled, which is the developer's responsibility and outside G1. The embedded
kernel is authenticated only if `release/releases/<version>/release.dsse.json` exists, verifies, and matches the embedded
bytes; otherwise the binary's embedded kernel is `DEVELOPMENT_UNSIGNED` and `gov version --trust` says so
(`build: development`). A development binary can install signed releases normally, but cannot install its own embedded
kernel as authenticated and can never produce `CERTIFIED` state for unsigned material.

## 5. Test fixture

Test-profile binaries (`--features trust-profile-test`) compile the test root and deny nothing test-signed. Certification
tests sign fixture releases at test time with committed test keys; unsigned fixtures (e.g.
`fixtures/update/previous-release/4.1.1`, harness v1's synthetic `prev-4.1.1`) are accepted as `DEVELOPMENT_UNSIGNED`.
A release pipeline check asserts that published binaries report `trust_profile: production`.

## 6. Classification summary

| Class | Signed by | Accepted by | Recorded trust level | Floors read from | Can become CERTIFIED | Doctor |
|---|---|---|---|---|---|---|
| Production certified | release + certification roles, production root | production and test binaries | `CERTIFIED` | installed kernel | yes | clean |
| Production uncertified / rejected | release role | production and test binaries | `AUTHENTICATED_UNCERTIFIED` / `AUTHENTICATED_REJECTED` | installed kernel | via a later certification statement | MEDIUM / HIGH |
| Legacy 4.1.2–4.1.5 | legacy-identity statement (certification role) over published digests | production and test binaries | `AUTHENTICATED_REJECTED` (`identity_source: legacy-identity`) | installed kernel | no | HIGH: update to a signed release |
| Development (unsigned) | nobody | production only with `--allow-unsigned-development`; test profile by default | `DEVELOPMENT_UNSIGNED` | production: embedded baseline (+ override gate for mutations); test: installed | **never** | production: HIGH D030 |
| Test | test keys | test-profile binaries only | `TEST` | installed kernel | **never** | n/a (test only) |
