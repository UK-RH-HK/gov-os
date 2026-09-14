# Output 4 — Canonical release-authentication architecture (RoT-1)

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 keeps the anchor, purposes, single authentication boundary and verify-and-use design the review confirmed.
> It adds the surface check (E7, `23`), freshness in authorisation (`24`), local trust gates (`27`), binary acceptance
> (`25`) and the legacy-path-occupation layout (`26`).

## 1. Alternatives evaluated

| Option | Description | Non-circular | Offline | Extensible | Provider-neutral | Verdict |
|---|---|---|---|---|---|---|
| O1 | Verify a source against its shipped manifest | **no** (E1) | yes | yes | yes | rejected |
| O2 | Binary-embedded digest registry only | yes | yes | **no** | yes | kept as components (TBM, compiled TPS and TSS) |
| **O3** | **Signed statements under compiled trust roots (RoT-1)** | yes | yes | yes | yes | **recommended** |
| O4 | Keyless signing with an identity provider and a transparency log | yes | partially | yes | **no** | rejected as root |
| O5 | Signed Git tags | partially | yes | yes | yes | rejected as root |
| O6 | Full TUF with an online timestamp role | yes | **no** for freshness | yes | yes | Not adopted wholesale. Revision 3 adopts rotation, thresholds, role separation, snapshot-style trust state, and locally anchored or expiring (OP-7 c) freshness in place of the online timestamp. |

## 2. Components

| Component | Proposed location (4.1.6) | Responsibility |
|---|---|---|
| Trust context (T0) | `runtime/src/trust/root.rs`, `purposes.rs`, `tbm.rs` | root chain, purpose table and whitelist, compiled TPS and TSS, Trust Base Manifest |
| Canonical JSON, DSSE, statements | `trust/jcs.rs`, `dsse.rs`, `statement.rs` | GOV-JCS-1, PAE, strict Ed25519, compiled schemas |
| Knowledge and trust state | `trust/state.rs` | S1–S12 (`17` §5) |
| **Anchors and freshness** | `trust/anchor.rs` | pins, confirmations, witnesses, freshness axis, operation-class gating (`24`) |
| **Constitutional Surface** | `trust/surface.rs` | inventory evaluation, E7, joins, precedence lattice, consumer register (`23`) |
| Eligibility and floor | `trust/eligibility.rs`, `trust/floor.rs` | E1–E10, effective policy, install authority (`19`) |
| **Trust gates** | `trust/trust_gate.rs` | local confirmations, decision pins, terminal challenge (`27`) |
| **Binary acceptance** | `trust/artifact.rs` | `verify-artifact` A1–A10, TBM checks (`25`) |
| Secure reader | `trust/secure_fs.rs` | `SecureDir`, VerifiedBlobs, link-count checks |
| Governed filesystem | `trust/governed_fs.rs` | PPS guard, including occupation entries and the transaction area |
| Authentication boundary | `trust/authenticate.rs` | the only constructor of `AuthenticatedRelease` |
| Authorisation | `trust/authorise.rs` | §4 |
| Install transaction | `trust/install_tx.rs` | journal, VTS registry, staging, union trust record, exchange, layout migration, recovery |
| Use-time snapshot | `kernel_trust.rs` v2 + `trust/snapshot.rs` | installation state, KernelSnapshot generation, EmbeddedSnapshot |
| **Layout** | `trust/layout.rs` | FORMAT, occupation entries, legacy detection, layout migration (`26`) |
| Producer tools | `release.rs`, `trust/publish.rs`, `trust/draft_policy.rs` | unsigned payloads; surface checker; TPS drafts; TSS publication |

Dependencies are as in revision 2: one pure-Rust Ed25519 implementation, `sha2`, and platform secure-open primitives.
D-0002's single binary is preserved.

## 3. Normative authentication algorithm

`authenticate(source, ctx, req) -> Result<AuthenticatedRelease, TrustError>`. **No byte is written to any Protected Path
before V12 and authorisation (§4) succeed.**

| Step | Action | Failure code |
|---|---|---|
| V0 | Resolve the source (environment may only select). | `KERNEL_SOURCE_NOT_FOUND` |
| V1 | Secure read-once of the whole tree into VerifiedBlob candidates; tree rules; link counts. | `RELEASE_TREE_INVALID` |
| V2 | Locate statements (release envelope, lineage candidate, bundle `trust/`, `artifacts/`). A present but failing statement never falls back. | `RELEASE_STATEMENT_MISSING` / `UNSIGNED_SOURCE_REFUSED` |
| V3 | Strict envelopes and canonical payloads (SV-1…SV-3). | `STATEMENT_MALFORMED` / `STATEMENT_TYPE_UNKNOWN` |
| V4 | Knowledge and effective state (`17` S1–S12) and freshness (`24`). A compiled root, TPS or TBM that does not verify refuses every authenticated operation. | `TRUST_ROOT_INVALID` / `PURPOSE_SEPARATION_VIOLATION` / `TRUST_POLICY_EQUIVOCATION` / `TRUST_STATE_EQUIVOCATION` / `TRUST_STATE_REGRESSION` / `BINARY_BELOW_TRUST_POLICY` |
| V5 | Purpose-bound signatures on the release statement (and candidate) (SV-4…SV-7). | `SIGNER_UNKNOWN` / `PURPOSE_NOT_GRANTED` / `SIGNER_REVOKED` / `SIGNATURE_INVALID` / `THRESHOLD_NOT_MET` |
| V6 | Compiled-schema validation (SV-8). | `STATEMENT_MALFORMED` |
| V7 | Type, stage and profile consistency (SV-9, SV-10). | `STATEMENT_TYPE_MISMATCH` / `TRUST_PROFILE_MISMATCH` |
| V8 | Identity, lineage, promotion (as revision 2). | `RELEASE_IDENTITY_MISMATCH` / `RELEASE_REPLAY_DETECTED` / `STATEMENT_LINEAGE_MISMATCH` |
| V9 | Content: every blob digest = `kernel.files`; recompute tree, manifest and component digests. | `RELEASE_DIGEST_MISMATCH` |
| V10 | Migrations: listed, equal, unique chain. | `MIGRATION_NOT_IN_STATEMENT` / `MIGRATION_DIGEST_MISMATCH` / `MIGRATION_CHAIN_AMBIGUOUS` |
| V11 | Compatibility using statement data only. | `RELEASE_INCOMPATIBLE` |
| **V11s** | **Surface:** evaluate the blob tree against the effective TPS's Constitutional Surface Inventory, with floor violations judged against the named TPS (`23` §6.3; E7). The result is part of the ARO. | (reported through E7 in §4) |
| V12 | Produce the `AuthenticatedRelease`: `{P, D, CI, signers, purpose, lineage, root version, blobs, candidate digest, trust_references, surface result}`. | — |

## 4. Authorisation (after V12, before any trusted write)

| Decision | Inputs | Defined in |
|---|---|---|
| Is the release eligible for this operation? | ARO (including the surface result), T0, effective TPS, negative set, VTS per-project record, installed verdict | `19` §6 (E1–E10) |
| Is the trust state sufficient, and is the machine fresh enough for C3? | trust-state axis, freshness axis, release-local references, OP-7 | `17` §7, `24` §4.3 |
| Which trust gate is required? | OP-3 mode, computed weakenings, declared changes, downgrade, computed policy reductions, evaluation, project strength | `27` §2 |
| What authorises it? | a **local** trust-gate confirmation bound to kind, `project_trust_id` and digests (terminal challenge or operator decision pin); never a repository record | `27` §3 |
| Is the actor authorised? | install-authority floor and actor level from the effective (floor-joined) policy; never the target | `19` §8 |
| Is the transaction possible now? | installation state (including occupation), transaction lock, VTS registry, platform primitives | `18` §5, §9 |

## 5. Use-time verification (`kernel_trust` v2)

**Algorithm:** `18` §6.

**Inputs:**
- installation state (FORMAT, layout, occupation);
- `governance/trust/release.dsse.json`;
- the installed kernel under `governance/trust/kernel/`, read once;
- T0 and the knowledge set;
- anchors;
- the VTS per-project record.

The lock is read only for cross-checks and hints.

| Check | Detects |
|---|---|
| installation state (`18` §9) | legacy layouts; partial installs, including removed occupation; honoured or foreign journals; unknown formats |
| statement verifies under T0 for a release purpose, lineage and profile | Git-delivered forged sets |
| installed file map ≡ statement | post-install tampering |
| E7 surface against the effective TPS | authentic content not registered, weaker than registered, or unclassified |
| eligibility E1–E6, E10 | historical, below policy, revoked, candidate, binary below policy, lineage, downgrade |
| trust state and freshness | restricts operation classes (`24` §4.3) |
| project-strength vector | overlay weakened outside a transaction |
| lock identity ≡ statement | edited lock |
| snapshot generation per unit of work (VU-11) | superseded snapshots in long-lived processes |

**Enforcement:**
- When `verified` is false, constitutional content comes from EmbeddedSnapshot ⊔ floors.
- Mutations fail closed with `KERNEL_TAMPERED`, `KERNEL_UNAUTHENTICATED`, `KERNEL_INELIGIBLE`, `INSTALL_STATE_PARTIAL`,
  `INSTALL_IN_PROGRESS` or the `24` §4.3 freshness codes.
- **Exempt remedies:** read-only diagnostics (C0), `gov recover`, `gov kernel reinstall` (same identity), and
  `gov update --apply` to an eligible target. The last is C3: it still needs an anchor and its trust gate.

There is no cross-process verdict cache.

## 6. Making "manufacturing trust" unrepresentable (API rules)

1. `AuthenticatedRelease` has private fields, no `Deserialize`, no public constructor, and is never persisted.
2. `install_tx` entry points accept `&AuthenticatedRelease` (or an authenticated restore target) and an `&Authorisation`,
   which can only be constructed from a consumed trust-gate confirmation read from the VTS. They mint the only
   `InstallTxToken`.
3. The lock writer accepts only the transaction's `InstalledRelease`; migrations have no lock operation.
4. Migrations and templates come from ARO blobs or the KernelSnapshot.
5. Tree hashing over paths is private to the producer.
6. `GovernedFs` is the only mutation API; `std::fs` mutation outside it fails an architecture test.
7. A `TrustGateConfirmation` type is constructible only by `trust_gate::confirm_on_terminal` or
   `trust_gate::from_decision_pin`. Nothing that parses repository records can produce one.
8. A `FreshnessProof`/`Anchor` type is constructible only by `anchor.rs` from the account database or verified witnesses.
   C3 entry points require it.
9. The policy loader is the only producer of effective policy values, and security decision points accept only values of
   the classes `floor`, `pinned`, `members` or `precedence` (`23` §6.5).
10. The `release_ingress` conformance family asserts rules 1–9 by source inspection and by interception or OS tracing
    across every CLI command (`02` §6).

## 7. Embedded baseline

`18` §7: an in-memory EmbeddedSnapshot named by the TBM, never materialised, no cache. A development binary's embedded
kernel is `DEVELOPMENT_UNSIGNED`.

## 8. Development and test paths

| Binary | Source | Acceptance | Policy root | Verdict |
|---|---|---|---|---|
| `gov` (production) | signed final | normal (E1–E10, freshness, trust gates) | installed snapshot if eligible | `AUTHENTICATED` / `ELIGIBLE` |
| `gov` (production) | signed candidate | evaluation flag + `evaluation_candidate` trust gate | installed snapshot; unregistered surface labelled | `ELIGIBLE_EVALUATION` |
| `gov` (production) | no statement | refused, or with `--allow-unsigned-development`: installs and writes `governance/trust/development.json` | EmbeddedSnapshot ⊔ floors; mutations need the override trust gate | `DEVELOPMENT_UNSIGNED`, `verified: false` |
| `gov` (production) | test-profile material | refused | — | `TRUST_PROFILE_MISMATCH` |
| `gov-test-profile` | test-signed | normal | installed snapshot | `TEST` |

## 9. Producer and signer interface

`07` §7.
