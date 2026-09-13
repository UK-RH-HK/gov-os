# Output 15 — Supersession of D-0007

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved.** D-0007 is not edited. D-0008
> remains PROPOSED (record status field `PROVISIONAL`, `in_effect: false`, no `chosen_option`, `supersedes: []`) until
> the owner answers its Human Decision Gate.

## 1. Decision

D-0008 **supersedes D-0007 in full** and restates the parts that remain correct. Partial amendment is rejected: a record
that is ACTIVE in some clauses and superseded in others leaves two authorities for one trust table.

The supersession takes effect only when the D-0008 approval gate is answered. Until then D-0007 remains ACTIVE and
unedited, and D-0008 does not list D-0007 in `supersedes`. Setting that link early would let a proposal change the
status of an authoritative record.

## 2. Diagnosis — what D-0007 got wrong

Verified against code by the architect (rev 1) and the independent review (`../4.1.6-review/06-D0007-D0008-REVIEW.md` §1):

| # | Error | Evidence |
|---|---|---|
| 1 | T1 decided by **agreement** among artefacts written from the untrusted source | `kernel.rs:248-256`, `lock.rs:12-35`, `kernel_trust.rs:125-169`; E4 |
| 2 | Incoming material had **no class**; release manifests treated as immutable release state | `update.rs:29-43`, `kernel.rs:124-154`, `build.rs:61-81`; E1 |
| 3 | An **authorisation** fact was read from the source | `update.rs:82-94`; E2 |
| 4 | The embedded anchor was consumed through a **mutable cache** | `kernel.rs:31-80`; E3 |
| 5 | Rules constrained **readers, not writers** | `update.rs:378-386`, `cli/src/main.rs:853`, `migrations/executor.rs:304-350`, `cit/mod.rs:704`; E5 |
| 6 | “Verified” conflated integrity and authenticity | doctor D029; `docs/ARCHITECTURE.md` §4.4a |
| 7 | T2 included Git-tracked records (gates, ledgers, registry) that a repository writer can forge, yet they were used for trust-relevant decisions | review §1 row 7 |
| 8 | D-0007 was agent-approved (R4, `human_approved: false`); a constitutional trust model needs owner approval | `spec/decisions/D-0007.yaml` |
| 9 | **Authenticity was conflated with currency**: an authentic older kernel was a valid policy root | review RV-H1; `../4.1.6-review/evidence/R1-legacy-kernel-floors.json` |

Error 9 was also present in D-0008 revision 1 and is corrected here.

## 3. Rules retained from D-0007

| D-0008 rule | Text | Change from D-0007 |
|---|---|---|
| (1) | An enforcement decision reads its floor from the highest **eligible** class only, joined with the Trust Policy floor. When that cannot be established, the embedded baseline is substituted explicitly and mutating operations fail closed. | “eligible” and “joined with the Trust Policy floor” added (currency) |
| (2) | *registered*, *approved*, *verified*, *eligible*, *certified*, *human_approved*, *authority*, *provenance* are facts of T0/T1/T2 only. A lower-class field carrying such a name is a request, recorded and ignored. | *eligible* and *certified* added |
| (3) | A project layer may specialise or strengthen a higher layer, never weaken it (POLICY_PRECEDENCE). | unchanged |
| (4) | Every refusal is typed and auditable; silence is never the mechanism. | unchanged |

Retained consequences: plugin registry authorisation; the kernel-trust boundary for security-critical consumers; governed
exceptions; governed `security_review_record`; the caller-declared acting role as a documented boundary.

## 4. Trust classes (replacement table)

| Class | D-0007 | D-0008 revision 2 |
|---|---|---|
| **T0** | — | Compiled into the running binary: root chain, purpose table and separation constraints, statement schemas, floor operators, newest Trust Policy and Trust State with referenced statements, historical-identity registry, EmbeddedSnapshot and its statement, trust-format readers |
| **T1** | embedded payload; installed kernel self-consistent with manifest and lock | **Authenticated material**: statements verified under the T0-rooted root chain for their purpose, and content whose bytes equal a verified release statement's file map (AuthenticatedRelease at ingress; KernelSnapshot at use) |
| **T1-E** | — | **Eligible authenticated release**: T1 release material satisfying the eligibility predicate (`19` §6). Only T1-E may be the current policy root. |
| T2 | OS-written project state | unchanged, with a boundary: Git-tracked T2 records are requests, not facts, against a repository writer for currency, freshness or downgrade decisions (rule 18); `framework.lock` is a T2 record of T1-E identity |
| T3 | verified registry and derived state | derived state is bound to the content identity it was built from (`18` VU-8) |
| **T4** | project configuration, plugin descriptors | + every repository- or user-writable artefact not currently verified: installed files before snapshot verification, lock fields, `governance/trust/` files before verification, VTS files before verification, caches, snapshots, journals, `.tx` directories |
| **T5** | CLI arguments, report fields, worker returns | + environment variables, source paths and their contents, bundles before authentication, downloaded files, descriptive release manifests |
| T6 | plugin and model data | + plugin-reported digests (`10` §5) |

## 5. New rules

The eight rules the owner required are marked **[O1]…[O8]**.

| Rule | Text | Owner requirement | Mechanism |
|---|---|---|---|
| (5) | **Derivation, not agreement.** Authenticity cannot be derived solely from mutually consistent files supplied by the candidate source. Class membership is established only by a verification chain to T0. | [O1] | `04` §3, `18` §1 |
| (6) | **Authenticity does not imply current-policy eligibility.** Eligibility, security floors and install authority are rooted in T0 and the protected Trust Policy lineage, never in the kernel being judged. Floors are strengthen-only joins and move down only through an explicit root-signed lowering accepted per project. | [O2] | `19` |
| (7) | **Trust state is monotonic and freshness-protected.** Negative lifecycle facts are sticky. Absence is never positive. A positive fact relaxes a control only with a freshness proof. Trust metadata is accepted only monotonically; a signed regression is refused. Time is used only for the optional freshness proof of OP-3 mode B. | [O3] | `17` |
| (8) | **The bytes verified are the bytes installed and enforced.** Installation writes verified buffers; enforcement reads only the verified in-memory snapshot; no mutable path is re-read after verification. | [O4] | `18` |
| (9) | **Key purposes and statement types are domain-separated.** Each statement type maps to one purpose, fixed in the binary; a key acts only within purposes the root grants, subject to compiled separation constraints; only release purposes confer kernel authenticity; historical identities are accepted only from T0. | [O5] | `05` |
| (10) | **Protected trust paths are written only by the install transaction.** Generic project mutation mechanisms (CIT, adoption, recovery, migrations, generators, installers) cannot create, modify, move or delete them. | [O6] | `18` §8, `02` §4 |
| (11) | **Incoming releases never define the authority required to install themselves.** Install-class authority is the maximum of the Trust Policy, the embedded kernel and the current eligible kernel. | [O7] | `19` §8 |
| (12) | **New trust-format state is never interpretable as verified by pre-RoT binaries**, and a binary never interprets a trust format it does not implement. | [O8] | `13` §3–§4 |
| (13) | **Statement facts only.** Certification, revocation, identity, compatibility and update-impact facts come only from signed statements; the same facts in descriptive files are requests. Signer-declared impact can add gates, never remove computed ones. | — | `07` §3, `19` §9 |
| (14) | **No fallback on failure.** An authentication or eligibility failure never falls back to a lower acceptance path. The development path is explicit and labelled, and is never eligible, certified or a production policy root. | — | `04` §8 |
| (15) | **Flags and environment cannot add trust.** They may select a source, opt into a lower labelled state, or narrow trust; they never add anchors, policies, state, certification, confirmation or eligibility. | — | `09` R-ENV |
| (16) | **No self-validation.** Statement schemas, floor operators and the purpose table come from T0, never from the material being verified. | — | `05` SV-8, `19` §4 |
| (17) | **Distinct facts, distinct authorities.** Release authenticity, release-candidate identity, independent verification result, certification state and current install eligibility are separate facts. The first four are signed by separate purposes; eligibility is computed. A signed candidate is never certified; an authentic historical release is never automatically current. | — | `05` §5, `17` §6, `19` §6 |
| (18) | **Repository-writable records are requests for currency.** Git-tracked gate records, ledgers and registries are evidence against A1/A3/A5, but never the basis of a currency, freshness or downgrade decision against a repository writer. | — | `20` §4, §9 |

## 6. Record changes on approval (4.1.6 implementation, not now)

| Record / document | Change |
|---|---|
| `spec/decisions/D-0008.yaml` | status ACTIVE, `state_class: AUTHORITATIVE`, `in_effect: true`, `human_approved: true`, `chosen_option`, `supersedes: [D-0007]`, owner answers to OP-1…OP-6, ceremony appendix (public data) |
| `spec/decisions/D-0007.yaml` | status SUPERSEDED, `superseded_by: [D-0008]`; content otherwise untouched |
| `spec/architecture/ARCH-0002.yaml` | status ACTIVE |
| record schema | add a `PROPOSED` status, or exclude `in_effect: false` from `RecordStore::active()` and the context compiler (RV-L4) |
| `docs/ARCHITECTURE.md` §4.4a | integrity, authenticity and eligibility distinguished; T0, T1-E added |
| doctor D003, D004, D029 wording; D030–D034 | per `09` §5 |
| release/distribution protocol | statements, promotion, trust state, bootstrap channels, OP-6 |

## 7. Revision history

| Revision | Commit | Outcome |
|---|---|---|
| 1 | `676dfce` | independent review `1c6027c`: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (RV-H1…RV-H4, RV-M1…RV-M8, RV-L1…RV-L4) |
| 2 | this amendment (uncommitted at authoring) | pending a fresh independent review; response matrix in `22` |
