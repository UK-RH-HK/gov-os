# Output 17 — Monotonic trust-state model (certification, withdrawal, revocation, root rotation)

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> New in revision 2. Addresses RV-H2 (CD-2) and the certification half of RV-M5 (CD-9). Normative keywords: MUST,
> MUST NOT, SHOULD.

## 1. The problem

A signature proves who said something. It does not prove that it is the latest thing they said.

Revision 1 accepted “the highest sequence among the statements presented”, so whoever controls presentation controls
freshness: a mirror (A1), a repository writer (A2), or an environment manipulator redirecting the store (A4). The
independent review derived three consequences:
- a stale CERTIFIED replayed without the later WITHDRAWN;
- a REJECTED statement omitted;
- revocations and root rotations stripped.

An offline verifier cannot learn what it was never given, so this model does not try to make omission impossible. It
makes omission **useless**. Nothing an attacker omits or replays produces a relaxation, and nothing already known can
be forgotten through the attacker's channel.

## 2. Principles (normative)

| ID | Principle |
|---|---|
| MS-1 | **Absence is never positive.** Missing certification, revocation, attestation or trust state never yields a state less restrictive than the corresponding negative fact would. |
| MS-2 | **Negative facts are sticky.** A verified revocation, REJECTED or WITHDRAWN statement known to any consulted knowledge source stays effective. It is lifted only by a root-signed Trust Policy `unrevokes` entry (revocation) or by a higher-sequence certification statement from the certification owner (certification). |
| MS-3 | **Relaxation requires proven freshness.** A positive lifecycle fact (CERTIFIED) may relax a control only with a freshness proof (§13). Without one, certification is informational. Under the recommended OP-3 mode A, no control is relaxable by certification at all. |
| MS-4 | **Monotonic acceptance.** Root versions, Trust Policy versions, Trust State sequences, revocation sequences and per-release certification sequences are accepted only if they do not regress against anything already known. A signed regression is a security event (`TRUST_STATE_REGRESSION`), not a fresher truth. |
| MS-5 | **Availability is untrusted; content is signed.** Which statements are present is attacker-influenced; what each says is not. Decisions use only the latter. |
| MS-6 | **Offline use is always possible.** Using an installed, eligible, authenticated release needs no network and no fresh trust state. |
| MS-7 | **The latest file in a repository is never freshness.** Repository- and bundle-supplied trust metadata is knowledge that can add facts. It never proves that no newer facts exist. |

## 3. Statement types and their counters

| Statement | Purpose (`05`) | Monotonic counter | Asserts | Can never assert |
|---|---|---|---|---|
| Trust root vN | `root` | `version` | keys, purpose grants, thresholds, revoked keys | anything about a release |
| **Trust Policy Statement (TPS)** | `trust-policy` | `policy_version` | floors, eligibility, install-authority floor, gating mode, lowering, unrevocation (`19`) | authenticity, certification |
| **Trust State Statement (TSS)** | `trust-state` | `sequence`, hash-chained | “these separately signed revocation, certification, verification-attestation and policy statements are the published state at sequence N”; optional expiry | any certification or revocation that is not itself a separately signed statement |
| Certification status | `certification-status` | `certification_sequence` per final statement digest | CERTIFIED / REJECTED / WITHDRAWN for one final statement digest | authenticity; CERTIFIED without an ACCEPTED attestation |
| Verification attestation | `verification-attestation` | bound by candidate digest | the independent verifier's verdict (ACCEPTED / REJECTED) for one candidate statement digest | certification |
| Revocation | `revocation` | `revocation_sequence` | `refuse_install` / `refuse_operation` for digests of releases, candidates, artifacts, profiles, attestations or certification statements | new trust |

**Why trust state is its own purpose.** The TSS is the only statement saying “this is the published set”. Separating it
from certification means:
- a stolen certification key cannot make its certification *referenced*, and therefore visible as CERTIFIED;
- a stolen trust-state key cannot create a certification; it can only reference existing signed ones.

A visible CERTIFIED therefore needs three independent signatures: verification attestation, certification status and a
trust-state reference.

## 4. Knowledge sources

| Source | Location | Who can write | Who can withhold | Role |
|---|---|---|---|---|
| **T0** | compiled into the binary: root chain, newest TPS, newest TSS with every statement it references, historical-identity registry | nobody at run time | nobody | knowledge + hard-minimum references |
| **Verifier Trust Store (VTS)** | per OS account, resolved from the account database — `getpwuid(getuid())` home on POSIX, the Known Folder API on Windows — **never** from `HOME`, `XDG_*` or `GOV_*`. Path: `<account-home>/.local/state/gov/trust/<trust_root_id>/` (platform equivalent elsewhere). | the same OS user (A3) | A3 | knowledge; lineage pin and confirmation (`06`); per-project installed-identity record (`20` §9) |
| **Project Trust Record (PTR)** | `governance/trust/state/` (Git-tracked, protected path) | repository writers (A2) | A2 | cross-machine knowledge |
| **Lock references** | `framework.lock` `trust_references` | A2 | A2 | hints only |
| **Bundle** | `trust/` inside a release bundle | the source (A1) | A1 | knowledge |
| **Refresh** | `gov trust refresh --from <file\|url>` | the supplier (A1/A5) | A1/A5 | knowledge |

Every statement from every source is verified (`05` SV-1…SV-10) before it enters the knowledge set **K**. Files that
do not verify are ignored with a typed warning and never counted. A source's writer can add only statements it
genuinely holds, delete, and withhold. It cannot forge.

## 5. Effective state algorithm (normative)

Runs in every process that makes a trust decision: once per ingress operation, and once per process at use time
together with the kernel snapshot (`18` §6).

| Step | Rule |
|---|---|
| S1 | Collect **K** = verified statements from T0 ∪ VTS ∪ PTR ∪ bundle ∪ refresh, as present for the operation. |
| S2 | **Root.** Effective root = the highest version reachable from the compiled chain by dual-threshold links. Links that do not chain are ignored (`TRUST_ROOT_INVALID` warning). |
| S3 | **Trust policy.** Effective TPS = the highest `policy_version` in K verifying under the effective root for `trust-policy`. A TPS whose `floor_schema_version` or any floor operator is unknown to this binary makes the binary `BINARY_BELOW_TRUST_POLICY` (read-only, `19` §4). |
| S4 | **Trust state.** A TSS T is *admissible* iff, for every lower-sequence TSS L in K: (a) `T.revocations ⊇ L.revocations`; (b) for every release digest in `L.certifications`, T has an entry whose certification statement's `certification_sequence` ≥ L's; (c) `T.references.root_version ≥ L.references.root_version`; (d) `T.references.trust_policy.policy_version ≥ L`'s; (e) `T.attestations ⊇ L.attestations`; (f) if `T.previous_state_digest` names a TSS in K, that TSS has sequence `T.sequence − 1`. Effective TSS = the highest admissible. A higher non-admissible TSS is a signed regression → `TRUST_STATE_REGRESSION`: not used, doctor CRITICAL, governed mutations refused until corrected. |
| S5 | **Negative set N** = every verified revocation target in K (standalone or referenced), ∪ every verified REJECTED/WITHDRAWN certification whose `certification_sequence` is the highest known for its digest, − targets named by any verified TPS `unrevokes`. |
| S6 | **Certification view** per final release digest (§6). |
| S7 | **Signed required minimums.** `RM_state` = max(T0 TSS sequence; every TSS sequence in K; every `trust_references.trust_state_sequence` in release statements in K; every `issued_under.trust_state_sequence` in certification statements in K). `RM_policy` and `RM_root` are formed the same way from policy and root references. |
| S8 | **Hint minimums.** `RH_state`, `RH_policy`, `RH_root` = max of the lock `trust_references` and the VTS per-project record. |
| S9 | **Staleness.** `STALE` if effective TSS sequence < `RM_state`, effective TPS version < `RM_policy`, or effective root version < `RM_root`. `HINT_MISMATCH` if not stale but effective < any `RH`. `REGRESSION` if S4 found one. Otherwise `CURRENT_KNOWN(sequence)`. |
| S10 | **Persist.** Newly verified statements from bundle, refresh or PTR are copied into the VTS. Statements the project lacks are written into the PTR **only** inside an install transaction or `gov trust refresh` (the PTR is a protected path, `18` §8). |

Staleness appears through signed references. Example: the installed release statement was signed when TSS 14 was
current (`trust_references.trust_state_sequence: 14`), but this verifier holds only TSS 12. An attacker cannot remove
that reference without replacing the release, and a replaced release is judged on its own references and on
eligibility (`19`).

## 6. Certification view

For a final release statement digest X:

| View | Condition | May it relax a control? |
|---|---|---|
| `REVOKED` | X ∈ N (any effect) | no; refuse per effect |
| `WITHDRAWN` / `REJECTED` | the highest-`certification_sequence` verified certification for X has that status | no; refused outright if TPS `gating.refuse_known_withdrawn` / `refuse_known_rejected` |
| `CERTIFICATION_UNREFERENCED` | a verified CERTIFIED statement for X exists in K, but no admissible TSS references it | no |
| `CERTIFIED_AS_OF(n)` | effective TSS n references verified CERTIFIED statement C for X; C references a verified ACCEPTED attestation for X's `promoted_from_candidate`; no negative fact for X | **no** |
| `CERTIFIED_CURRENT(n)` | `CERTIFIED_AS_OF(n)` ∧ freshness proof (§13) ∧ trust state `CURRENT_KNOWN` | only under OP-3 mode B, and only to skip the update gate (§7) |
| `NOT_CERTIFIED` | none of the above | no |

For a candidate digest: `CANDIDATE_UNATTESTED`, `CANDIDATE_ATTESTED_ACCEPTED` or `CANDIDATE_ATTESTED_REJECTED`
(informational; candidates are never production-eligible, `19` §7).

Every surface — `gov status`, context packets, lock `verdict_at_install`, doctor, gate text — shows the view with its
`n`.

## 7. Trust-state requirement by operation

| Operation | Trust state required | Role of certification | Negative facts |
|---|---|---|---|
| Read-only diagnostics | none | displayed | displayed |
| Governed use of the installed release (including project-state mutations) | none. `STALE` → doctor D032 HIGH; `REGRESSION` → CRITICAL and mutations refused | displayed | `refuse_operation` → `KERNEL_INELIGIBLE` |
| `init`, `adopt migrate --batch 0` | not `STALE`; `HINT_MISMATCH` → gate | a Human Decision Gate (or init acknowledgement) bound to the statement digest is always required; init is never unattended | refuse `refuse_install`; refuse known REJECTED/WITHDRAWN when the TPS says so |
| `update --apply` | not `STALE`; `HINT_MISMATCH` → gate | mode A (recommended): gate always. Mode B: `CERTIFIED_CURRENT`, no computed weakening (`19` §9), no declared breaking change and no declared gate ⇒ the gate may be skipped | as above |
| `update --rollback`, snapshot restore, journal recovery that downgrades | not `STALE` | gate always (`20` §4) | as above |
| `kernel reinstall` (same statement digest) or re-attestation | none | none | `refuse_install` → refused |
| Evaluation-candidate install | not `STALE` | gate + explicit flag always | revoked candidates refused |

`STALE` is resolved only by supplying the missing signed metadata. `gov trust refresh --from <file>` works offline with
a copied file. **There is no override for `STALE` at ingress**: an override would let whoever strips metadata choose
the outcome.

## 8. Revocation state

- Revocations accumulate (S5). Nothing an attacker supplies removes one: an admissible TSS must contain every revocation
  that any lower known TSS contained.
- A revocation delivered alone, before any TSS references it, is effective immediately (MS-2). Restricting needs no
  freshness.
- Unrevocation exists only as a root-signed TPS `unrevokes` entry naming the revocation statement digest. It is
  permanent; re-revocation needs a new revocation statement.
- Effects:
  - `refuse_install` applies at ingress, rollback and restore;
  - `refuse_operation` also applies at use time: the release is `INELIGIBLE`, policy comes from the embedded baseline
    joined with the floor, and mutations are refused except remedies.
- A security-relevant revocation of a final release SHOULD come with a TPS raising `eligibility.min_release_sequence`.
  Binaries compiled afterwards then refuse the release even where no revocation statement ever arrives.

## 9. Root-rotation state

- Root versions are monotonic and dual-threshold chained (unchanged from rev 1).
- Every release, TSS, TPS and certification statement carries `trust_references.root_version`, the root version
  current at signing. A verifier whose effective root is lower is `STALE` for ingress (`TRUST_ROOT_STALE`) and cannot
  verify keys introduced later.
- Key revocation protects a verifier once it holds the root version that removes the key. Statements signed only by a
  removed key are invalid whatever their references say; genuine ones are re-attested (`05` §8).
- **Residual RS-1** (§15): a thief of a later-removed key can sign statements referencing an old root version. A
  verifier that never received the removing root version cannot tell them apart. What still holds there:
  - the stolen key is purpose-limited (`05`);
  - ingress still needs a gate (mode A);
  - eligibility floors come from at least the compiled TPS;
  - certification cannot be manufactured, because it needs three purposes.

## 10. Replay protection

| Replay | Binding that defeats it |
|---|---|
| Statement of lineage X presented to lineage Y | `trust_root_id` in every payload (`05` SV-10) |
| Test statement presented to production | `trust_profile` in every payload |
| Statement of one type presented as another | payloadType ↔ purpose ↔ `_type` fixed in the binary; PAE binds the payloadType |
| Certification for release A applied to release B | full `release_statement_digest`, plus `release_id` and `version` equality |
| Attestation for candidate A applied to candidate B | full `candidate_statement_digest` |
| Final promoted from a different candidate | `promoted_from_candidate` must equal the attestation's candidate digest, and the candidate's `kernel.tree_digest` must equal the final's (`04` V8) |
| Older TSS presented as current | admissibility (S4) plus signed required minimums (S7) |
| Older TPS presented to lower floors | monotonic `policy_version`; lowering needs a higher version (`19` §10) |
| Older root presented | dual-threshold chain plus monotonic version |
| Gate answered for digest A reused for digest B | gate records bind `release_statement_digest`, and both digests for a rollback |
| CERTIFIED reused after WITHDRAWN | per-digest `certification_sequence` ordering (S5) |
| Release statement reused for other content | V9 full file map; `release_id` derived from the tree digest |

## 11. Rollback of trust metadata

| Attack | Result |
|---|---|
| A1 serves an older TSS, TPS or root | knowledge only; the effective state is the highest admissible known; staleness is detected wherever a signed reference is higher |
| A1 omits the newest TSS | if no signed reference is higher, the older state is used. `CERTIFIED_AS_OF(n)` relaxes nothing in mode A; negatives already known remain. Residual RS-1. |
| A2 deletes `governance/trust/state/` | no effect on machines with a VTS or a newer T0. Fresh clones fall back to T0 plus references in the signed statements still present; they are `STALE` whenever the installed release was signed under newer state than T0 holds. |
| A2 edits lock `trust_references` | hints only: can cause `HINT_MISMATCH` (a gate); cannot hide anything signed |
| A3 deletes or rewrites the VTS | forgetting on that machine only; rewritten files that do not verify are ignored |
| A4 sets `HOME`, `XDG_CONFIG_HOME` or `GOV_*` | no effect; the VTS location comes from the account database |
| A trust-state key thief publishes a higher TSS that omits revocations | non-admissible on every verifier knowing the lower TSS (S4) → `TRUST_STATE_REGRESSION`. Verifiers knowing nothing lower see only the freeze residual. |

## 12. Offline operation

- **Using an installed eligible release:** no network, no fresh state (MS-6).
- **Installing from a local bundle:** works offline; the bundle carries TSS, TPS and root links; gates required (mode A).
- **Air-gapped propagation:** `gov trust export` writes a signed-metadata bundle (statements only); `gov trust refresh
  --from <file>` imports it.
- **Mode B offline:** gate-free updates cannot be used offline beyond the TSS expiry. By design, freshness is exactly what
  is being proven.

## 13. Freshness proof (OP-3 mode B only)

A freshness proof exists for effective TSS n iff all of these hold:
- (a) TSS n has a non-null `expires_at`;
- (b) the local clock is earlier than `expires_at`;
- (c) the local clock is later than the highest `issued_at` of any verified statement in K (coarse clock-rollback
  detection);
- (d) the trust state is `CURRENT_KNOWN`.

Mode B trusts the local clock for exactly one decision: whether the update gate may be skipped. A3 or A4 controlling the
clock can defeat it, which is why mode B is owner-optional and not recommended (`21` OP-3).

Time never removes trust: expiry of a TSS never invalidates an installed release, authenticity or a revocation.

## 14. Recovery semantics

| Situation | Recovery |
|---|---|
| VTS missing or corrupt | Rebuilt from T0 ∪ PTR ∪ bundles; corrupt files ignored; lineage confirmation re-requested per OP-6. |
| PTR deleted (A2 or accident) | The next install transaction or `gov trust refresh` rewrites it from VTS, T0 or a bundle. Until then, fresh clones may be `STALE`, which fails closed for ingress only. |
| `STALE` on a machine | Supply metadata that meets the required minimum (`gov trust refresh --from`). Read-only and governed use continue. |
| `TRUST_STATE_REGRESSION` observed | Mutations refused (possible trust-state key compromise). The owner rotates the `trust-state` purpose and publishes a correcting admissible TSS with a sequence above the regressive one. |
| Erroneous TSS publication (e.g., revocation omitted at sequence n) | Verifiers that saw n−1 reject n. The publisher issues a correct n+1; verifiers that saw only n accept it because it is a superset. |
| Trust-state key lost | Root grants a new key; the next TSS continues the sequence and chains to the last published digest. |
| Certification key stolen | Root removes the key; the publisher stops referencing forged certifications; forged certification digests are revoked. A forged CERTIFIED would already have needed two further keys. |
| Verification-attestation key stolen | Root removes the key; attestations alone certify nothing. |
| Revocation key stolen | Attacker can only revoke (denial of service). Root removes the key; a TPS `unrevokes` the forged revocations. |
| Release-final key stolen | `05` §9. |

## 15. Accepted residuals (explicit)

| ID | Residual | Why accepted | Bound |
|---|---|---|---|
| RS-1 | A verifier that never received a newer TSS, root version or revocation cannot know it exists (fresh machine, stripped repository, older binary, no refresh). | Offline verification (G5) forbids requiring an online oracle. | It cannot produce a relaxation (mode A), remove a known negative fact, lower floors below the compiled TPS, or certify. |
| RS-2 | Mode B trusts the local clock to skip an update gate. | Owner-optional automation convenience. | Disabled by default; exploitable only by A3/A4. |
| RS-3 | A3 can delete the VTS on its own machine. | Same-user code execution is inside the account boundary. | Forgetting on that machine only; no forging. |
