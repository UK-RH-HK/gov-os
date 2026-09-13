# Output 12 — Architecture Correction Delta

The delta **amends** RoT-1; it does not replace it. Everything in §0 is retained unchanged. After these corrections the
architect re-issues the pack and D-0008/ARCH-0002 for a fresh independent review. This reviewer does not edit the pack,
D-0008 or ARCH-0002.

## 0. Retain unchanged

Compiled trust-root chain with dual-threshold rotation; role/payloadType binding for release, certification, revocation
and profile statements; DSSE + Ed25519 strict + GOV-JCS-1; full file map and component/migration digests; the single
`authenticate` constructor and `AuthenticatedRelease` capability; quarantine rules; the install transaction and journal;
the lock as a record; the in-memory embedded baseline; the development and test separation; profile statements as
provenance only; transport independence; the E1–E5 closures; RT-01…RT-30.

## CD-1 — Currency floor and strengthen-only floors (closes RV-H1)

| Pack file | Change |
|---|---|
| `00-OVERVIEW.md` §3 | add property **Currency**: “is this authenticated material acceptable as the policy root, or as a reason to relax authorisation, for this binary now?” |
| `03-TRUST-CHAIN.md` §1 | kernel_trust v2 gains a currency step after authenticity |
| `04-AUTHENTICATION-ARCHITECTURE.md` §5 | add checks: (a) installed `release.sequence` ≥ the T0 **operational floor** compiled into the binary (new `KERNEL_BELOW_OPERATIONAL_FLOOR`) — failure ⇒ `verified:false`, embedded baseline, mutations refused except `update --apply` to a target at or above the floor; (b) **strengthen-only floors**: for every key that the *embedded* `POLICY_PRECEDENCE` marks immutable or strengthen-only, the effective value is the stronger of installed-authenticated and embedded-authenticated; (c) `trust_level` ordering defined, with `verified` in production requiring `trust_level ≥` the T0 minimum |
| `04` §8 | `minimum_trust_level` becomes a T0 constant (production `AUTHENTICATED_UNCERTIFIED`); kernel and overlay may only raise it |
| `06-BOOTSTRAP.md` §6, `08-FRAMEWORK-LOCK.md` §5, `11-MIGRATION-PLAN.md` Phase 1.3 and Phase 4, `13-COMPATIBILITY.md` | legacy kernels become `LEGACY_IDENTIFIED`: identity is recognised (for update-source identification, reinstall of the same identity, rollback evidence) but **never the policy root**. Floors from the embedded baseline; operations limited to update, read-only diagnostics and override; D030 CRITICAL. Replace the false claim in Phase 1.3 with the diff evidence (`evidence/legacy-kernel-security-diffs.txt`). |
| `09-INTEGRATION-REQUIREMENTS.md` R-RB, R-REC, §3.3 | every restore (explicit rollback, journal swap-back, recovery, adoption restore) re-authenticates and applies currency and downgrade rules. A decrease in sequence or trust level requires the gate unless the current state is already unverified. The ledger is evidence, never the bound. |
| `01-THREAT-MODEL.md` §6 | add TH-R1; amend TH-06/07/08 status |
| `15-D-0007-SUPERSESSION.md` §4.2, `D-0008.yaml` rationale | add rule (11) “Authenticity is not currency”; state that Git-tracked T2 records (gates, ledger, registry) are A2-writable requests for any currency decision |
| `12-ACCEPTANCE-TEST-PLAN.md` | add RV-A15 (A2+A3), A18, A19, A27; R1 must flip on 4.1.6 |

## CD-2 — Monotonic lifecycle facts and freshness linkage (closes RV-H2)

| Pack file | Change |
|---|---|
| `07-RELEASE-ENVELOPE-SPEC.md` §4, `schemas/revocation-statement.schema.json` | revocation entries gain `effect: decertify` (a certification withdrawal or rejection that gating depends on) alongside `refuse_install`/`refuse_operation`; negative lifecycle facts travel only here, under the compiled floor + high-water |
| `schemas/certification-statement.schema.json` | add required `issued_under_revocation_sequence` (integer); status enum keeps `CERTIFIED`, `REJECTED`, `WITHDRAWN` for audit, but `REJECTED`/`WITHDRAWN` must be mirrored by a `decertify` or `refuse_install` revocation entry |
| `04` V13 and §8 | CERTIFIED relaxes a gate only if the effective revocation sequence ≥ `issued_under_revocation_sequence` and no `decertify` entry names the statement digest; otherwise treat as UNCERTIFIED (gate). REJECTED gating must never depend on the presence of an optional statement. Every signed candidate that fails verification receives a `refuse_install` or `decertify` entry (or OP-4 option (a)). |
| `05-KEY-MANAGEMENT.md` §5 | the high-water store location must not be selectable by `XDG_CONFIG_HOME`/`HOME` alone, or an env-selected store counts as absent. Release statements record the root version and revocation sequence current at signing (`signing.root_version`, `signing.revocation_sequence`), so any repository carrying a statement also asserts the minimum metadata a verifier must hold. A verifier that cannot see that metadata reports D032 CRITICAL and refuses gate relaxation and installs. |
| `01` §5, `14-RISKS.md` RK-02, `05` §7 | restate the residual: repository-carried metadata can be stripped by A2 and the user store reset by A3/A4; compromise recovery is durable only via binary upgrade (and via the signing-time metadata references above) |
| `12` | add RV-A10, A17, A21, A22, A23, A24 |

## CD-3 — Only the release role confers kernel authenticity (closes RV-H4)

| Pack file | Change |
|---|---|
| `05` §1 table, payloadType table | remove `legacy-identity` from the certification role and from the runtime envelope allowlist |
| `08` §5, `06` §6, `11` Phase 1 | legacy identity digests (4.1.2–4.1.5: version, tree digest, manifest digest, commit) become **T0 constants** compiled into the binary, reviewed in the ceremony record; never read from bundles, `governance/trust/` or any envelope. If an auditable signed copy is wanted, it is signed by the release role under the root threshold and is informational only. |
| `15` §4.2, `D-0008.yaml` | add rule (12) “Only the release role (or root threshold) confers T1 authenticity on kernel content; certification, revocation and profile statements annotate or lower trust” |
| `12` | add RV-A20 |

## CD-4 — Byte binding at use time (closes RV-H3)

| Pack file | Change |
|---|---|
| `04` §2 and §5 | `TrustedKernel` is an immutable in-memory snapshot. Read each file once, digest that buffer, compare with the statement, parse from the same buffer; no component re-opens kernel paths after verification. Long-lived processes hold the snapshot or re-verify before each constitutional read. |
| `04` §5, `07` §5.1 | use-time tree rules equal quarantine rules, including refusal of symlinks and non-regular files in `governance/`, `governance/kernel/`, `governance/trust/` and their contents; component-wise no-follow opens |
| `09` §3.2 | staging directories are created exclusively with unpredictable names and verified by `lstat` or no-follow; files created with `O_EXCL`; directory entries fsynced after renames; templates and migrations read from `AuthenticatedRelease` memory |
| `12` | add RV-A14, A25 (use `evidence/R2b-use-time-toctou.py`, 20/20 trials), A37, A38 |

## CD-5 — Path-based writer guard and completed ingress map (closes RV-M1)

- `02-INGRESS-MAP.md`: add I-34 (adoption batch rollback, `gov recover` batch branch), I-35 (CIT write/move/delete and
  snapshot restore), I-36 (A7/A11 `kernel_ok`), I-37 (adapter freshness), I-38 (partial install), I-39 (trust refresh and
  user store), I-40 (older binaries), I-41 (journal as adversarial input). Correct the I-10 description.
- `02` §3 and `04` §4: add a governed filesystem layer refusing write, rename and delete under `governance/kernel/**`,
  `governance/trust/**`, `governance/framework.lock` without an install-transaction token. The conformance proof is
  write interception across every CLI command, not symbol inspection alone.
- `09`: CIT and adoption executors refuse those paths at planning and execution; adoption batch-0 rollback delegates to
  install-transaction recovery; CIT, adoption and `rebuild-memory` honour the transaction lock.

## CD-6 — Installed-state determination (closes RV-M2)

`04` §5: installed-for-trust = any of lock, `governance/kernel/`, `governance/trust/`, install journal present. Any
partial state is `UNAUTHENTICATED` with the embedded baseline and mutations refused. The policy root is never an
unverified directory, including for commands opened without the install requirement.

## CD-7 — Authority from T0 for every ingress (closes RV-M3)

`09` §1 step 2 and `04` §8: authority for init, adopt batch 0, update, reinstall, rollback, recover and override is read
from the embedded authenticated kernel (T0), strengthened by the installed authenticated kernel if present. Never from
the target or an unauthenticated installed kernel. Add rule (14) to D-0008.

## CD-8 — Make older binaries fail closed (closes RV-M4)

`08` §3 and `13` row 4: lock 2.0.0 drops `kernel_manifest_hash` and `release_hash` under their 1.1.0 names (carry them as
`kernel.manifest_digest`/`kernel.tree_digest` with the `sha256:` prefix). A ≤4.1.5 binary then sees no lock hash and
fails closed (`kernel_trust.rs:156-169`). Document mixed-binary teams. Update `adapters.rs` freshness to the statement
digest.

## CD-9 — Candidate stage and verification attestation (closes RV-M5)

`07` §3: add signed `release.stage: candidate | final`; production `init`/`update` of `candidate` require an explicit flag
and gate. Either add a `verification` statement type (a verifier key under its own role, attesting the report digest and
verdict), or require the certification statement to embed a verifier-signed verdict. Final releases may then use release
threshold 2 (release key + verification attestation) as an OP-2 choice. Rewrite OP-4 as “stage field, candidate role, or
mandatory candidate revocation”.

## CD-10 — Bootstrap anchoring (closes RV-M6)

`06` §2.1: at least two fingerprint channels **not hosted with the releases**. `06` §2.5 and OP-6: if confirmation is not
mandatory per init, require it once per user trust store or CI environment (a narrowing pin), and amend TA-5 accordingly.
`08` §3: specify `TRUST_ROOT_LINEAGE_MISMATCH` (fail closed, no re-pin) when a binary of another lineage opens an existing
project. Withdraw “none of them changes the architecture” (`00` §5).

## CD-11 — Host-verified profile integrity (closes RV-M7)

`10-RETRIEVAL-PROFILE-TRUST.md` §5: the host computes plugin, runtime and model digests itself. Plugin-returned digests are
informational (T6). Change detection uses content digests or a host-held verified-record digest, not size/mtime. The
runtime environment (hash-locked packages) is re-verified at registration, rebuild and plugin start, or runs from a
read-only content-addressed store.

## CD-12 — Migration authorisation and chain shape (closes RV-M8)

`04` §8 and `09` R-UPD-6: the runtime computes strength-reducing overlay changes from the migration operations (against
the embedded `POLICY_PRECEDENCE` and DATA_SENSITIVITY semantics) and requires a gate listing them, regardless of
signer-declared `breaking`. `07` §3 and V10: the migration set forms a unique chain (one migration per `from_version`);
statement `breaking`/`human_gate` must equal the file values.

## CD-13 — Low-severity fixes (RV-L1…L4)

Fix the RV-L1 inconsistencies (V15 reference; RT-05(c) versus schema; path character set versus GOV-JCS-1; `release_id`
wording; duplicated migration fields; key id recomputation and duplicate keys; algorithm-migration schema or remove the
claim; OP-5 gating; revocation and certification matching fields; corrupt compiled root fails closed). Make the test
profile a separate binary target or crate (RV-L2). Define deterministic statement inputs, the post-build append-only file
set of a release directory, and move the design commit off the rejected candidate branch (RV-L3). Add a `PROPOSED` record
status, or exclude `in_effect: false` from `active()`, with the D-0008 approval change (RV-L4).

## Re-review entry criteria

1. CD-1…CD-12 reflected in the pack, schemas, D-0008 rationale (rules 11–14) and ARCH-0002.
2. `12-ACCEPTANCE-TEST-PLAN.md` includes RV-A04, A05, A10, A14–A38 (or equivalents) with expected codes.
3. The pack's claims about legacy kernel content are corrected with the diff evidence.
4. OP-3, OP-4 and OP-6 are restated as in `07-OWNER-OPTIONS-REVIEW.md`, so the owner answers options whose security
   meaning is stable.
