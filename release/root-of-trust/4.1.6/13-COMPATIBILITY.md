# Output 13 — Backwards-compatibility consequences

| Area | Change | Who is affected | Mitigation |
|---|---|---|---|
| Unsigned sources | production binaries refuse sources without a release statement (`UNSIGNED_SOURCE_REFUSED`) | developers installing from a working tree; scripts using synthetic kernels (harness v1 HV-11, `fixtures/update/previous-release/4.1.1`) | test-profile binary accepts them as `DEVELOPMENT_UNSIGNED`; production `--allow-unsigned-development` with override gate; canonical checkout at a signed tag authenticates normally |
| Historical releases 4.1.2–4.1.5 | installable only through the legacy-identity statement as `AUTHENTICATED_REJECTED` | harness v2 NV-03/NV-08/NV-13; operators pinning old releases | gate flow unchanged; doctor HIGH recommends update |
| Self-declared certification | `manifest.json certification.status` no longer affects the update gate | anyone relying on editing the block to skip gates (the E2 vulnerability) | intended; certification statements replace it |
| `framework.lock` | schema 1.1.0 → 2.0.0 (additive fields, identity semantics); `release_commit` only from the statement | tools parsing the lock | all 1.1.0 field names retained; older binaries read `version`/`release_hash`/`kernel_manifest_hash` and report D005 version mismatch as today |
| New tracked directory `governance/trust/` | added to consumer repositories | repository reviewers; `.gitignore` rules | small signed JSON files; documented in the consumer contract |
| `gov kernel trust` output | new fields; `verified` now also requires authenticity (production) | scripts testing `verified` | unchanged for genuine signed and legacy installs; `false` exactly in the E1–E5 attack states and unsigned production installs |
| `gov release verify` | `ok` requires a verifying signature; output adds trust verdict | the verifier convention citing `release verify` for 4.1.x payloads | historical payloads report `identity_source: legacy-identity`, `trust_level: AUTHENTICATED_REJECTED` |
| `gov release build` | emits `release.statement.json`; never signs; refuses private key material | release owner workflow | signing step documented (`07` §7) |
| Update refusals for trust reasons | `ok: false` instead of `ok: true, applied: false` | automation expecting soft refusals | only trust codes change; gate-pending responses keep the 4.1.5 shape |
| `gov kernel reinstall --source <arbitrary>` | must authenticate to the installed statement digest | ad-hoc restores | reinstall from the matching release or bundle |
| Rollback of snapshots made by 4.1.5 | authenticated via legacy identity; unknown digests refused | projects with tampered or non-release snapshots | intended |
| Environment variables | `GOV_KERNEL_SOURCE` removed; `GOV_CANONICAL_ROOT` no longer a schema fallback; cache never trusted | developer shells, CI | documented deprecations |
| Direct kernel readers | all go through `TrustedKernel` | internal only | architecture test |
| Dependencies | + one pure-Rust Ed25519 crate | D-0002 single binary | `ldd` stays libc-only |
| Performance | + one signature verification per process; hashing as today | none measurable | no cross-process cache |
| Platforms | `.gitattributes -text` for payload directories | Windows checkouts with `core.autocrlf` | prevents digest drift |
| Records | D-0007 → SUPERSEDED by D-0008 on approval; ARCH-0002 added | narrative docs citing D-0007 | D-0008 restates D-0007 rules (1)–(4) verbatim |
| Frozen harnesses | expected results per `12` §4 (HV-11 intended refusal on the production profile) | independent verifier | classification rule in `12` §4 |
