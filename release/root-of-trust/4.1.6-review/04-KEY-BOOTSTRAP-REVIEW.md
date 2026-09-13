# Output 5 — Key and Bootstrap Review

## 1. Key roles (`05-KEY-MANAGEMENT.md` §1)

| Role | Signs | Review | Verdict |
|---|---|---|---|
| root (3 keys, threshold 2) | trust-root versions; key revocation | TUF dual-threshold rotation (previous **and** new sets) blocks single-key re-rooting; compiled monotonic version | sound |
| release (1 active + 1 standby, threshold 1) | release and artifact statements | a registered standby key can sign immediately, so it needs **equal** custody, not just separate custody. With threshold 1, one token or host compromise yields release authenticity for every consumer until binaries update (see §4) | sound in shape; custody wording must be tightened (OP-2) |
| certification (1 + standby, threshold 1) | certification, release revocation, **legacy identity** | legacy identity confers kernel authenticity and policy-root status (`08` §5, `06` §6). That is a release-authenticity power held by a role with weaker custody and no hardware requirement. A certification-key thief can list an arbitrary tree digest as “4.1.5” and get `verified:true` with floors read from that tree. Revocation by this role is acceptable (it only removes trust; worst case is denial of service). | **unsound for legacy identity** (RV-H4) |
| profile | profile statements | provenance and integrity only; never authorisation | sound |
| test | test statements (test-profile binaries only) | keys deliberately public; production deny-list; production refuses `trust_profile: test` everywhere | sound; see §6 on feature unification |

The payloadType → role table is fixed in the binary; the algorithm comes from the root key record, not the envelope; role
key sets must be disjoint. All sound.

**Missing invariant (add to D-0008):** only the release role (or the root threshold) may confer T1 authenticity on
kernel content. Certification, revocation and profile statements may only annotate authenticated content or lower its trust.

## 2. Key identifiers and representation

- `keyid = ed25519:<sha256(raw public key)>`. The verifier must **recompute** the id from `public_key`, refuse any
  mismatch, and refuse the same public key under two ids. Otherwise a ceremony mistake (or a root compromise below
  threshold) lets one key count twice towards a threshold. The pack defines the id format but not the check (RV-L1).
- Trust-root id = SHA-256 of the canonical v1 payload: a good lineage name.
- “Future algorithm migration … role policy requiring signatures from keys of each listed algorithm” (`05` §4) cannot
  be expressed in `schemas/trust-root.schema.json` (roles carry only `key_ids`, `threshold`) (RV-L1). It is not
  blocking for 4.1.6.

## 3. Rotation, revocation, re-attestation

| Mechanism | Verdict | Note |
|---|---|---|
| Routine rotation via root N+1 | sound | — |
| Root rotation (both thresholds) | sound | — |
| High-water marks (user store `$XDG_CONFIG_HOME/gov/trust-state.json` + lock) | **not durable** | both are writable (A2 lock; A3 store), and `XDG_CONFIG_HOME` makes the store env-selectable (A4). The pack admits the compiled floor is the only hard minimum. The consequence is not carried into the threat model (RV-H2). |
| Release revocation (certification role, monotonic sequence) | sound in format; **not durable after ship** against A2/A4 | RV-H2 |
| Key revocation only via a new root version | sound | — |
| Re-attestation (statement digest excludes signatures) | sound | confirmed: `statement_digest` = SHA-256 of the payload bytes (`07` §1; example) |

## 4. Compromise and loss playbooks (`05` §7)

The steps are correct, but the stated residual (“offline consumers that never receive N+1”) is too narrow. Any consumer
evaluating a repository without the user trust store (a fresh clone, CI, a second machine), or with a redirected
`XDG_CONFIG_HOME`, will accept a statement from the stolen key once A2 deletes `governance/trust/root/N+1.json` and
`governance/trust/revocations.dsse.json` from the repository. **Recovery from a release-, certification- or profile-key
compromise is durable only through binary upgrade**, not repository-delivered metadata. D-0008 must say so, and the
owner should weigh it in OP-2 (release threshold 2 for final releases is a cheap mitigation).

Loss playbooks (one root key, standby, threshold loss → re-bootstrap with re-signing) are coherent.

## 5. Private signing material

- Rules (never in repository, history, bundles, CI logs or secrets, consumer repositories, `.governance-runtime/`) plus
  producer refusal and a conformance scan: sound.
- **E** today: `grep` for `PRIVATE KEY` / `openssh-key-v1` over the working tree and full history finds only detection
  patterns (`framework/policies/SECURITY_POLICY.yaml` and the release copies, `runtime/src/security/secrets.rs`,
  `05-KEY-MANAGEMENT.md`, `release/verification/4.1.4/heldout-v3/harness_v3.py`). `examples/make_example.py` generates
  an **in-memory** Ed25519 key and writes only the public envelope; the committed `release.dsse.example.json` carries
  only `keyid`/`sig`.
- Generated fixtures: test fixtures signed at test time with the committed test keys are test-profile by construction.
  Acceptable only because the production deny-list and profile refusal exist (AC-H3).

## 6. Test, development and production keys

| Concern | Verdict |
|---|---|
| Test root compiles only with `trust-profile-test` | sound in intent. **Hazard:** a cargo feature on the shared `gov-runtime` crate can be unified into the shipped binary by a workspace build that also builds test targets (`resolver = "2"` in `Cargo.toml` separates dev-dependency features only when tests, examples and benches are not built). Use a separate binary target or crate for the test profile, a `compile_error!` guard for the release pipeline, and the artifact-statement `trust_profile_feature` check (RV-L2). |
| Production refuses test material in statements, roots, locks, `governance/trust/` | sound |
| Development binary (`cargo build` from a checkout) | compiles `trust/production/`; embedded kernel `DEVELOPMENT_UNSIGNED` unless the statement verifies; cannot produce CERTIFIED for unsigned material. A **fork** with a substituted `trust/production/` is also `trust_profile: production`, under a different lineage; only a lineage pin detects it (RV-M6). |
| `--allow-unsigned-development` in production | sound: floors stay on the embedded baseline and mutations need the override gate. A2 writing `development.json` + an arbitrary kernel yields `DEVELOPMENT_UNSIGNED` / `verified:false` → baseline floors, so no escalation. |

## 7. Bootstrap (review area 6)

**Is there a hidden circular dependency “binary trusts release → release supplies keys → keys authenticate release”?**
No. The root the binary checks against is compiled from `trust/production/` and never taken from a release. A bundle
may only *extend* the compiled chain (dual-threshold verified). The embedded kernel is authenticated against the same
compiled root.

The loop that remains is **source tree → binary (root + embedded kernel)**. That is the TCB by assumption (`01` §4
TA-1), and only an out-of-band fingerprint comparison breaks it (TA-5). Three weaknesses:

1. **Channels.** `06` §2.1 requires “at least two channels that do not share an attacker with the release host”, yet
   lists (a) the D-0008 record appendix and (b) the release protocol on `main`, both hosted with the releases. Only (c)
   is independent (RV-M6).
2. **OP-6 default.** With no mandatory confirmation, automated installs pin whatever lineage the obtained binary
   carries (trust on first use), so TA-5 does not hold for them. Either TA-5 is weakened explicitly, or confirmation
   happens once per user trust store / CI environment (narrowing only) (RV-M6, `07-OWNER-OPTIONS-REVIEW.md`).
3. **Lineage mismatch at runtime.** `08` §3 says the lock's `trust_root` lineage “must equal running binary's” but gives
   no code or behaviour. A binary of another lineage opening an existing project must fail closed
   (`TRUST_ROOT_LINEAGE_MISMATCH`), never re-pin (RV-M6).

**Dev, test and unsigned modes remain mechanically distinct from production-authenticated state:** yes. They have
separate trust levels, `verified:false` in production for `DEVELOPMENT_UNSIGNED`, floors from the baseline, D030 HIGH,
no CERTIFIED path, and a production refusal of test profiles. Subject to RV-L2.
