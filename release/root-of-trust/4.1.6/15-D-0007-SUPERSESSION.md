# Output 15 — Supersession of D-0007

## 1. Decision

D-0008 **supersedes D-0007 in full** and restates the parts that remain correct. Partial amendment was rejected: a
decision record that is ACTIVE in some clauses and superseded in others leaves two authorities for the same trust table,
which is the kind of ambiguity that produced the circularity.

The supersession takes effect only when the D-0008 approval gate is answered. Until then D-0007 remains ACTIVE and
unedited; D-0008 is PROPOSED and pending approval (record status field `PROVISIONAL`, `in_effect: false`, no `chosen_option`) and does not list D-0007 in `supersedes` (setting that link early would let a lower-trust
record change the status of an authoritative one).

## 2. Diagnosis (summary of `00-OVERVIEW.md` §4)

D-0007's T1 ("installed kernel whose payload matches `KERNEL_MANIFEST.json` and whose manifest matches
`framework.lock.kernel_manifest_hash`") is satisfied by construction at install time, because the installer writes both
references from the incoming bytes. Class membership was decided by agreement among repository-writable artefacts, the
incoming source had no class, authorisation facts were read from the source, the embedded anchor was consumed through a
mutable cache, and the rules constrained readers rather than writers.

## 3. What is retained verbatim

- Rule (1): an enforcement decision reads its floor from the highest class only; when that cannot be established, the
  embedded baseline is substituted explicitly and mutating operations fail closed.
- Rule (2): *registered*, *approved*, *verified*, *human_approved*, *authority*, *provenance* are facts of the top classes
  or OS-written project state only; a lower-class field carrying such a name is a request, recorded and ignored.
- Rule (3): a project layer may specialise or strengthen a higher layer, never weaken it (POLICY_PRECEDENCE).
- Rule (4): every refusal is typed and auditable; silence is never the mechanism.
- Consequences: plugin registry authorisation, `trusted_root` for security-critical consumers, governed exceptions,
  governed `security_review_record`, caller-declared acting role as a documented boundary.

## 4. What changes

### 4.1 Trust classes (replacement table)

| Class | D-0007 | D-0008 |
|---|---|---|
| **T0** | — | **Trust anchors compiled into the running `gov` binary**: trust-root metadata chain, revocation floor, statement schemas, embedded kernel bytes and embedded statements |
| **T1** | embedded payload; installed kernel self-consistent with manifest and lock | **Authenticated framework material**: bytes whose digests are bound by a statement verifying under T0 for the required role, not revoked, identity and compatibility checked — at ingress as an `AuthenticatedRelease`, at use as installed files ≡ installed statement. Includes verified certification, revocation and profile statements |
| T2 | OS-written project state | unchanged; `framework.lock` is a T2 **record** of T1 identity, never a source of it |
| T3 | verified registry/derived state | unchanged |
| **T4** | project configuration, plugin descriptors | + every repository- or user-writable artefact not currently authenticated: installed kernel files, `KERNEL_MANIFEST.json`, lock fields, `governance/trust/` files before verification, caches, snapshots |
| **T5** | CLI arguments, report fields, worker returns | + environment variables, `--source` paths and their contents, release directories and bundles before authentication, downloaded files, descriptive release manifests |
| T6 | plugin and model data | unchanged |

### 4.2 New rules

- **(5) Derivation, not agreement.** Class membership is determined by a verification chain to T0. Agreement among
  artefacts is integrity evidence only and never establishes T1.
- **(6) Writers consume authentication.** Every write to a T1 location (installed kernel, trust statements, lock identity
  fields, embedded materialisation, snapshot restore) and every migration execution consumes an `AuthenticatedRelease`
  produced by the single authentication boundary before any byte leaves quarantine.
- **(7) Statement facts only.** Certification, revocation, signer role, release identity, compatibility and update-impact
  facts are T1 statements; the same facts in a descriptive file are T5 requests, recorded and ignored.
- **(8) No fallback on failure.** An authentication failure never falls back to a lower acceptance path. Absence of a
  statement may be accepted only through the explicit, permanently labelled development path, which never yields a
  production-authenticated or certified state and never becomes the policy root in a production binary.
- **(9) Flags and environment cannot add trust.** They may select a source or opt into a lower labelled state; they never
  add, replace or extend anchors.
- **(10) No self-validation.** Trust statements are validated with schemas from T0, never with schemas from the material
  being authenticated.

## 5. Record changes on approval (4.1.6 implementation)

| Record / document | Change |
|---|---|
| `spec/decisions/D-0008.yaml` | status ACTIVE, `human_approved: true`, `supersedes: [D-0007]`, owner parameters and ceremony appendix |
| `spec/decisions/D-0007.yaml` | status SUPERSEDED, `superseded_by: [D-0008]` (content otherwise untouched) |
| `spec/architecture/ARCH-0002.yaml` | status ACTIVE |
| `docs/ARCHITECTURE.md` §4.4a | "verified" split into integrity and authenticity; T0 added |
| doctor D029 wording | "constitutional policy read from an **authenticated** kernel", with D030–D033 |
| release/distribution protocol | §8 release manifest → signed release statement; §9, §12, §16 updated; bootstrap section added |
