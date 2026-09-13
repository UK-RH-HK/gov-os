# Independent Root-of-Trust Architecture Review — RoT-1 for Governance OS 4.1.6

| | |
|---|---|
| **Verdict** | **ROOT_OF_TRUST_ARCHITECTURE_REJECTED** |
| Reviewer role | Fresh Independent Governance OS Root-of-Trust Architecture Reviewer (no architect, builder or verifier context carried) |
| Date | 2026-09-13 |
| Reviewed | `release/root-of-trust/4.1.6/` (00–16, `schemas/`, `examples/`, `evidence/`), `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md`, as committed in `676dfce` |
| Rejected baseline | `release/4.1.5-rc1`, tag `v4.1.5-rc1`, commit `da9c8518d3fddba6f37bafb4d046ca313335ec1f` |
| Also read | D-0007; the 4.1.5 independent re-verification report (§12–§13) and V-H3 evidence; the implementation in `runtime/build.rs`, `kernel.rs`, `kernel_trust.rs`, `lock.rs`, `release.rs`, `update.rs`, `init.rs`, `adopt.rs` (batch 0, scanner, A3, A7, A11), `recovery.rs`, `project.rs`, `policy.rs`, `policy_precedence.rs`, `authority.rs`, `records.rs`, `context/mod.rs`, `exceptions.rs`, `cit/mod.rs` (file operations), `migrations/{framework,executor,classify}.rs`, `adapters.rs`, `memory/indexer.rs`, `retrieval/mod.rs`, `cli/src/main.rs` |
| Not modified | No runtime, CLI, kernel, migration, fixture, test, released payload, verifier artefact, architecture-pack file, D-0007, D-0008 or ARCH-0002. Additions: this directory only. **D-0008 is not approved by this review**; approval remains the product owner's. |

## 1. Executive summary

RoT-1's core is sound and should be kept. Trust originates in public keys compiled into `gov`. Offline keys sign a
canonical statement that binds the complete kernel file map. One authentication boundary runs before any trusted write.
Manifests, locks, caches, environment and transport are never trusted. The embedded baseline comes from memory, and
development/test material cannot reach production-authenticated or certified state. I reproduced E1–E5 exactly; RoT-1
closes all five at the root. The digest-continuity claims hold for every legacy release.

But RoT-1 closes only **authenticity**. It does not yet close the rest of the defect class that four rejections exposed.
Four HIGH findings remain; each lets a lower-trust, stale or unverified input manufacture a current higher-trust fact:

| ID | Finding | Evidence |
|---|---|---|
| **RV-H1** | **No currency floor at use.** An older or legacy *authenticated* kernel delivered by Git, adoption-snapshot restore or forged journal + lock becomes the `verified:true` policy root. `minimum_trust_level` is read from the kernel being judged. Legacy kernels are **not** security-equivalent, contrary to the pack. | **executed**: on the genuine 4.1.2 kernel an L3 role passes `update --apply` authority and `resume`; on 4.1.5 both `AUTHORITY_DENIED`; both `verified:true` |
| **RV-H2** | **Lifecycle facts are replay- and omission-unsafe.** A stale CERTIFIED can be replayed without its WITHDRAWN (gate skipped: E2 with signed data); a REJECTED statement can be omitted (`init` ungated); revocations and root rotations can be stripped by A2 or reset by A4 on any machine without the user store. | design, with the E2 consequence reproduced |
| **RV-H3** | **Verified bytes ≠ enforced bytes.** `TrustedKernel` “over installed dir” re-reads files after verification. | **executed**: a same-user racer swapped the policy 0.11 ms after verification; two restricted records were indexed and stayed retrievable while `kernel trust` said `verified:true` and doctor D003/D004/D029 were ok |
| **RV-H4** | **A non-release role confers kernel authenticity.** The legacy-identity statement, which makes a kernel an authenticated policy root, is signed by the certification role and is not restricted to the compiled copy. | design |

Eight MEDIUM findings: unguarded writers (adoption rollback, CIT `move_file`/`delete_file`) missing from the ingress map;
partial-install fail-open; install authority read from the target; pre-RoT-1 binaries still trusting RoT-1 projects;
verification and candidate status not distinct; bootstrap channels co-hosted and OP-6 trust on first use; profile
integrity relying on plugin-reported digests; signed migrations removing project strengthening without a gate.

The correction is an **amendment**, not a redesign: `11-CORRECTION-DELTA.md` CD-1…CD-13.

## 2. Method and independence

1. Read the whole pack, D-0007, D-0008, ARCH-0002, the 4.1.5 report and V-H3 evidence, and every implementation file
   listed above. No architect claim was accepted without a code citation or an executed check.
2. Confirmed the probe binary represents the rejected candidate: `git diff --stat da9c851 HEAD -- runtime cli framework
   migrations tools Cargo.toml Cargo.lock` is empty.
3. **Re-executed** the architect's E1–E5 in fresh scratch directories: identical outcomes, including regenerated hash
   `aa8fb66a…` and `never_index_classes: [secret]` after each attack (`evidence/E1-E5-reproduction-output.txt`).
4. **Re-executed** the digest-continuity check for 4.1.2/4.1.3/4.1.4/4.1.5: tree digest = published `release_hash`;
   manifest digest = `KERNEL_MANIFEST.json` hash; schema-valid; DSSE sign, verify and tamper rejection; the example
   payload regenerates byte-identically (`evidence/continuity-check-4.1.2-4.1.5.txt`). Also confirmed the harness v2
   worktree `8ad06be` has framework/migrations/tools identical to 4.1.2 release commit `f709834`.
5. **New probes** (scratch only): R1 legacy-kernel floors; R2 (preliminary) and R2b use-time TOCTOU
   (`evidence/README.md`).
6. Authored 40 held-out architecture attacks (`08`), then assessed coverage.

## 3. Answers to the sixteen review areas

| # | Area | Verdict | Where |
|---|---|---|---|
| 1 | Non-circular trust root | **holds for authenticity**. Anchors outside release contents; no self-manufactured anchors; manifests, locks and caches never trusted; lock never creates trust. **Fails for currency and lifecycle freshness** (RV-H1, RV-H2); lock 1.1.0 fields keep old binaries circular (RV-M4) | `03` §1–2 |
| 2 | Source authentication before installation | **holds** for init, adopt batch 0, update, reinstall, embedded/bundle/local/remote sources. **Gaps:** recovery via adoption batch rollback and CIT file operations (unmapped writers, RV-M1); rollback bounded by an A2-writable ledger (RV-H1); install authority from target (RV-M3) | `02` |
| 3 | Post-install integrity separation | correctly separated, and V-H2 preserved in shape; **not byte-bound** (RV-H3); partial-install policy root unspecified (RV-M2) | `03` §3, `05` §2 |
| 4 | Signed release statement | canonical serialisation, identity, digests, migrations, compatibility, signer, algorithm binding: **sound**. No field outside the signature influences a decision (manifests ignored). Gaps: no stage field (RV-M5), no signing-time metadata references (CD-2), migration chain uniqueness (RV-M8), consistency nits (RV-L1) | `03` L3, `10` |
| 5 | Key architecture | roles, disjointness, thresholds, TUF rotation, re-attestation, test/prod separation: **sound**. Legacy identity on the wrong role (RV-H4). Revocation and rotation not durable against A2/A4 (RV-H2). Standby custody, key-id recomputation, feature unification (RV-L1, RV-L2) | `04` |
| 6 | Bootstrap | **no hidden release→keys→release loop**. Residual TCB loop broken only by the out-of-band fingerprint; two of three channels co-hosted; OP-6 makes that trust on first use; lineage mismatch unspecified (RV-M6). Dev, test and unsigned states stay mechanically distinct and never certified | `04` §6–7 |
| 7 | Cache and fallback safety | **sound**: in-memory embedded baseline; marker never evidence; stale, copied or replaced cache cannot become a root (RT-17) | `02` I-11/I-12 |
| 8 | Rollback / snapshot authenticity | snapshots authenticated: **sound**. Downgrade policy ledger-bound; adoption snapshots unmapped; recovery lacks currency rules (RV-H1, RV-M1) | `05` §6 |
| 9 | Git / transport independence | transport is not the root; offline verification works; tags are not identity: **sound**. A compromised repository can still change the *current* trust state (RV-H1, RV-H2) | `03` §4 |
| 10 | Old release treatment | legacy records cannot confer CERTIFIED: **sound**. Replay as current through gov refused; through Git or restore **accepted**; legacy content is weaker (executed R1) | `03` §6 |
| 11 | Certification separation | authenticity ≠ certification, and signed ≠ certified: **sound**. Candidate status and verifier acceptance are not mechanically represented (RV-M5) | `03` §5 |
| 12 | D-0007 → D-0008 | diagnosis confirmed in code, plus two errors the architect did not name. Full supersession is right. D-0008 needs rules (11)–(14). No conflicting authority today; latent PROVISIONAL-as-active pattern (RV-L4) | `06` |
| 13 | Existing security controls | V-H1, V-M1, gates bound to digests, precedence, sensitivity, authority, ledger, immutability are preserved by design; no regression introduced. **V-H2 remains bypassable by racing** (RV-H3, already present in 4.1.5). Legacy acceptance would reopen authority floors (RV-H1). Signed migrations can weaken project sensitivity (RV-M8) | `09` AC-I2 |
| 14 | Reference retrieval profile | supply-chain shape correct; model choice stays non-constitutional (D-0006) and signatures are provenance only (D-0007). Use-time verification relies on plugin-reported digests (RV-M7) | `01` TH-20 |
| 15 | Key-ceremony options | OP-1, OP-2, OP-3, OP-4, OP-6 are security-material; OP-3 and OP-4 depend on CD-1/CD-2; OP-5 is not material while informational. None approved here | `07` |
| 16 | New adversarial tests | 40 attacks; 8 covered as written; 2 executed against 4.1.5 | `08` |

## 4. Output map

| # | Required output | File |
|---|---|---|
| 1 | Independent architecture-review report | `00-REVIEW-REPORT.md` |
| 2 | RoT-1 Threat-Coverage Matrix | `01-THREAT-COVERAGE-MATRIX.md` |
| 3 | Privileged-Ingress Coverage Matrix | `02-PRIVILEGED-INGRESS-COVERAGE.md` |
| 4 | Trust-Chain Review | `03-TRUST-CHAIN-REVIEW.md` |
| 5 | Key/Bootstrap Review | `04-KEY-BOOTSTRAP-REVIEW.md` |
| 6 | TOCTOU / transaction-safety review | `05-TOCTOU-TRANSACTION-REVIEW.md` |
| 7 | D-0007 → D-0008 review | `06-D0007-D0008-REVIEW.md` |
| 8 | Owner-option review OP-1…OP-6 | `07-OWNER-OPTIONS-REVIEW.md` |
| 9 | New held-out architecture attack register | `08-HELDOUT-ATTACK-REGISTER.md` |
| 10 | Implementation acceptance criteria | `09-IMPLEMENTATION-ACCEPTANCE-CRITERIA.md` |
| 11 | Blocking findings ranked | `10-BLOCKING-FINDINGS.md` |
| 12 | Architecture correction delta | `11-CORRECTION-DELTA.md` |
| — | Evidence (scripts, verbatim outputs) | `evidence/` (index: `evidence/README.md`) |

## 5. Consequences for the owner and the next iteration

- D-0008 should **not** be presented for approval in its current form. After CD-1…CD-13 it should come back to a fresh
  review, then to the owner's gate with OP-3, OP-4 and OP-6 restated.
- No builder work on 4.1.6 should begin; the architecture, the schemas and the owner options would change underneath it.
- The two executed findings (RV-H1 evidence R1, RV-H3 evidence R2b) are present in the 4.1.5 implementation today.
  4.1.5 is already rejected and immutable, so they raise no new release action. They must be carried into the 4.1.6
  acceptance suite (AC-C2, AC-E1).

## 6. Verdict

**ROOT_OF_TRUST_ARCHITECTURE_REJECTED**

Rejection basis: four HIGH architecture-level findings (RV-H1…RV-H4). Two are demonstrated by execution. All four belong
to the trust-authenticity class RoT-1 was required to close in full. No CRITICAL finding: the non-circular anchor,
authentication boundary, transaction and E1–E5 closures are accepted as the base for the correction delta.
