# Output 7 — Release envelope and statement specification

Machine-readable schemas: `schemas/`. Worked example: `examples/release-statement.payload.example.json`.

## 1. Layers

```text
release.dsse.json  = DSSE envelope (JSON)
  payloadType      = "application/vnd.agentic-engineering-os.release-statement.v1+json"
  payload          = base64( GOV-JCS-1 canonical bytes of the release statement object )
  signatures[]     = { keyid: "ed25519:<hex>", sig: base64( Ed25519( PAE(payloadType, payload_bytes) ) ) }

PAE(type, body)    = "DSSEv1" SP LEN(type) SP type SP LEN(body) SP body      (LEN = ASCII decimal byte length)
statement_digest   = "sha256:" + hex( SHA-256( payload_bytes ) )             (signatures excluded → stable across re-signing)
```

DSSE (Dead Simple Signing Envelope) is used unchanged, so any conforming implementation can cross-verify. The signing
algorithm is bound twice: by the trust-root key record (authoritative) and by `signing.algorithm` inside the payload
(checked equal, V7).

## 2. Canonical serialisation profile GOV-JCS-1

RFC 8785 (JSON Canonicalization Scheme) with these restrictions, enforced by the verifier (V3):

1. UTF-8, no BOM, no insignificant whitespace, no trailing bytes.
2. Object member names are ASCII printable (0x20–0x7E); sorted by RFC 8785 rules (byte order for ASCII); **duplicate
   names are an error** (a non-strict JSON parser silently keeping the last value is not acceptable).
3. Numbers: integers only, in `[-(2^53-1), 2^53-1]`; no floats, exponents or `-0`.
4. Strings: RFC 8785 escaping; all string values must be Unicode NFC; paths additionally obey §5.
5. Depth ≤ 32; payload ≤ 4 MiB.
6. The verifier decodes, parses strictly, re-serialises, and requires byte equality with the decoded payload.

Value formats: digests `sha256:<64 lowercase hex>`; versions SemVer 2.0.0; timestamps RFC 3339 UTC `YYYY-MM-DDTHH:MM:SSZ`
(informational only — no security decision uses a signer-supplied time); commits 40 lowercase hex.

## 3. Release statement (payload) fields

| Field | Type | Req | Semantics | Verified at |
|---|---|---|---|---|
| `_type` | const `https://agentic-engineering-os/statement/release/v1` | ✓ | domain separation (with payloadType) | V7 |
| `trust_profile` | `production` \| `test` | ✓ | must match the binary profile | V5 |
| `framework` | const `agentic-engineering-os` | ✓ | framework identity | V8 |
| `release.version` | SemVer | ✓ | equals `KERNEL.yaml` `version` | V8 |
| `release.release_id` | `<framework>@<version>#<16 hex>` | ✓ | hex = first 16 of `kernel.tree_digest`; binds identity to content (anti-replay) | V8 |
| `release.sequence` | integer ≥ 1 | ✓ | strictly increasing across all signed releases of the framework; downgrade/equivocation detection | V12 |
| `release.release_commit` | 40 hex | ✓ | commit the payload was reproduced from | provenance |
| `release.release_tag` | string | ✓ | e.g. `v4.1.6-rc1` | provenance |
| `release.released_at` | timestamp | ✓ | informational; used as `built_at` of the derived `KERNEL_MANIFEST.json` | — |
| `manifest_version` | const `1` | ✓ | statement format version | V7 |
| `signing.role` | const `release` | ✓ | intended role | V5/V7 |
| `signing.algorithm` | `ed25519` | ✓ | intended algorithm | V5/V7 |
| `compatibility.cli` | `{min, max_exclusive}` SemVer | ✓ | CLI versions allowed to install/operate | V11 |
| `compatibility.runtime` | `{min, max_exclusive}` | ✓ | runtime versions | V11 |
| `compatibility.kernel_contract_version` | integer | ✓ | binary must support it | V11 |
| `compatibility.supported_from_versions` | SemVer[] | ✓ | update sources | V11 |
| `compatibility.index_version` | string | ✓ | expected derived-index format | V11 |
| `compatibility.schema_versions` | map name → SemVer | ✓ | equals `KERNEL.yaml` `schema_versions` | V9 (KERNEL.yaml digest) + V11 |
| `kernel.tree_rules` | const `gov-tree-v1` | ✓ | §5 | V1 |
| `kernel.file_count` | integer | ✓ | size of `files` | V9 |
| `kernel.files` | map relpath → digest | ✓ | **every** kernel payload file except `KERNEL_MANIFEST.json` | V9 |
| `kernel.tree_digest` | digest | ✓ | §5.3; equals the 4.1.x `release_hash`/`payload_hash` definition | V9 |
| `kernel.manifest_digest` | digest | ✓ | §5.4; equals the 4.1.x `kernel_manifest_hash` definition | V9 |
| `components` | map name → digest | ✓ | digest of the sub-map for each `KERNEL.yaml` `payload_dirs` entry plus `KERNEL.yaml` (e.g. `schemas`, `policies`, `constitution`, `roles`, `migrations`, `tools`) | V9 |
| `security_critical` | relpath[] | ✓ | files whose change alters constitutional floors (declarative, audited; all are in `files`) | V9 (membership) |
| `migrations[]` | `{id, from_version, to_version, path, digest, breaking, human_gate}` | ✓ | every migration in the tree | V10 |
| `update_impact` | `{breaking_changes[], human_gates[], required_index_rebuilds[]}` | ✓ | inputs to authorisation | V15 |
| `documents` | map name → digest | ✓ | `RELEASE_NOTES.md`, `ROLLBACK.md` (non-privileged, digest-bound) | report only |
| `profiles[]` | `{profile_id, profile_version, statement_digest}` | — | reference profiles compatible with this release | `10` |
| `provenance` | `{release_branch, builder, reproduced_from_commit, source_tree}` | ✓ | descriptive, but signed | — |

Not in the statement, by design: certification status (separate statement, issued later), binary digests (binaries are
built after signing; artifact statement), any timestamp used for decisions, any machine path.

## 4. Other statements

| Statement | Role | Key fields |
|---|---|---|
| **Certification** (`schemas/certification-statement.schema.json`) | certification | `release_id`, `version`, `release_statement_digest`, `status` (`CERTIFIED`\|`REJECTED`\|`WITHDRAWN`), `sequence`, `verifier_report {path, digest}`, `verdict {path, digest}`, `issued_at`, `supersedes` (previous certification statement digest or null) |
| **Revocation** (`schemas/revocation-statement.schema.json`) | certification | `sequence`, `revoked_releases[] {release_id, statement_digest, effect: refuse_install\|refuse_operation, reason}`, `issued_at` |
| **Artifact** (`schemas/artifact-statement.schema.json`) | release | `release_id`, `release_statement_digest`, `artifacts[] {name, target, digest, size}`, `build {toolchain, reproducible}` |
| **Legacy identity** (`schemas/legacy-identity-statement.schema.json`) | certification | `releases[] {version, release_id, release_commit, tree_digest, manifest_digest, certification_status, verifier_report {path, digest}}` for 4.1.2–4.1.5 |
| **Trust root** (`schemas/trust-root.schema.json`) | root | `trust_profile`, `framework`, `version`, `keys`, `roles`, `revoked_keys[]`, `revocation_floor_sequence`, `issued_at` |
| **Profile** (`schemas/profile-statement.schema.json`) | profile | see `10-RETRIEVAL-PROFILE-TRUST.md` |

## 5. Kernel tree canonical digest (`gov-tree-v1`)

### 5.1 Tree rules

1. Members are regular files. Symbolic links, hard-link tricks resolving outside the tree, devices, FIFOs and sockets →
   `RELEASE_TREE_INVALID` (4.1.5 silently skips non-regular files in both `copy_dir` and `hash_tree`; RoT-1 refuses).
2. Relative path: `/`-separated, NFC, no leading `/`, no `.`, `..` or empty segment, no `\`, no NUL, segment ≤ 255 bytes,
   path ≤ 1024 bytes.
3. No two paths equal under Unicode case folding (portable to case-insensitive filesystems).
4. Only `KERNEL_MANIFEST.json` at the tree root is excluded; it is derived (§5.4).
5. Content digest = SHA-256 of the raw bytes; no line-ending or encoding normalisation. The canonical repository adds
   `.gitattributes` `-text` for `framework/`, `migrations/`, `tools/`, `release/releases/` so checkouts on any platform
   reproduce identical bytes.
6. File mode is not part of the digest; the installer writes payload files non-executable.
7. Limits: ≤ 10 000 files, ≤ 64 MiB total, ≤ 16 MiB per file.

### 5.2 File map

`files = { relpath: "sha256:<hex>" }`. For continuity with 4.1.x, the **tree digest input** uses the bare hex form
(exactly the map hashed by `util::hash_tree` today): `hexmap = { relpath: "<hex>" }`.

### 5.3 Tree digest

`tree_digest = "sha256:" + hex(SHA-256(GOV-JCS-1(hexmap)))` — byte-identical to 4.1.x `payload_hash` / `release_hash`
(e.g. 4.1.5 → `sha256:962f9848…a314b`).

### 5.4 Manifest digest and derived `KERNEL_MANIFEST.json`

`manifest_digest = "sha256:" + hex(SHA-256(GOV-JCS-1({framework, version, files: hexmap, payload_hash: <tree hex>})))` —
identical to 4.1.x `kernel::manifest_hash`. The installer writes `KERNEL_MANIFEST.json` deterministically from the
statement (`built_at = release.released_at`), so it is byte-identical on every machine and never depends on install time.

### 5.5 Component digests

For each component `c`: `components[c] = "sha256:" + hex(SHA-256(GOV-JCS-1({p: hex | p ∈ hexmap, p starts with c + "/"})))`;
`components["KERNEL.yaml"]` is the file digest.

## 6. Bundle layout

```text
agentic-engineering-os-<version>/
├── release.dsse.json                   # authoritative (signed)
├── kernel/**                           # payload; KERNEL_MANIFEST.json optional and ignored for trust
├── certification/<sequence>.dsse.json  # 0..n
├── trust/root/<version>.json           # optional newer root chain links
├── trust/revocations.dsse.json         # optional newest revocation statement
├── artifacts.dsse.json                 # optional binary digests
├── manifest.json, manifest.yaml        # descriptive only, unsigned, never used for decisions
└── RELEASE_NOTES.md, ROLLBACK.md       # digest-bound via documents
```

Archive form: POSIX tar (ustar/pax), optionally compressed. Extraction refuses absolute paths, `..`, links, devices,
duplicate members and anything violating §5.1 before authentication begins.

## 7. Producer and signer interface

1. `gov release build --version V` → writes the payload, descriptive manifests and `release.statement.json` (the
   canonical unsigned payload), never a signature.
2. External signer (offline, any DSSE-conformant Ed25519 tool; a reference `gov-sign` binary may be provided but is not
   part of the consumer TCB) → `release.dsse.json`.
3. `gov release attach-signature DIR ENVELOPE` → verifies the envelope over `release.statement.json` under the compiled
   trust root before placing it; refuses otherwise.
4. `gov release verify DIR` → runs V0–V13 in report-only mode and prints the full verdict, including trust level and
   certification.
