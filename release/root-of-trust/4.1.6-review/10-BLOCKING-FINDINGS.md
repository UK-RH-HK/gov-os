# Output 11 — Blocking Findings (ranked)

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 4 | RV-H1, RV-H2, RV-H3, RV-H4 |
| MEDIUM | 8 | RV-M1 … RV-M8 |
| LOW | 4 | RV-L1 … RV-L4 |

**No CRITICAL finding.** The trust anchor itself is not circular: compiled public keys, offline private keys, a DSSE
signature over a canonical payload that binds the complete file map, a single authentication boundary before any trusted
write, the lock as a record only, and the embedded baseline served from memory. Nothing an adversary writes to a source,
repository, cache, snapshot, environment or transport can become authentic.

**Four HIGH findings block acceptance.** Each is an instance of the class RoT-1 was commissioned to close: a
lower-trust, stale or unverified input manufacturing a current higher-trust fact. HIGH findings are ranked by
exploitability and impact; MEDIUM and LOW are listed in ID order.

---

## RV-H1 — HIGH — Authenticity without currency: an older or legacy authenticated kernel becomes the policy root

**Statement.** `kernel_trust` v2 (`04` §5) accepts any installed set whose statement verifies under T0, whose files
match it, and which is not revoked. It has no version, sequence or floor check. V12 downgrade protection runs only
inside `authenticate`. Production `verified` admits `AUTHENTICATED_REJECTED` and legacy identities (`04` §5; `06` §6:
legacy floors “read from installed kernel”; `11` Phase 4: legacy “operates”, D030 only HIGH). `minimum_trust_level` is
read from the kernel being evaluated (`04` §8). Explicit rollback is bounded by `spec/reports/framework-updates.jsonl`
(R-RB-2), which A2 can write.

**Evidence.**
- **E** `evidence/R1-legacy-kernel-floors.json`: same 4.1.5 binary, same L3 role (`change-controller`). On the genuine
  4.1.2 kernel, `update --apply` passes authority (stops at `HUMAN_GATE_REQUIRED`) and `resume` succeeds. On the 4.1.5
  kernel both return `AUTHORITY_DENIED`. Both kernels `verified:true`. The 4.1.5 binary reads floors from a verified
  installed kernel exactly as RoT-1 does for a legacy-identified one.
- **E** `evidence/legacy-kernel-security-diffs.txt`: 4.1.2 `AUTHORITY_POLICY` lacks `update_apply`, `resume_control` and
  about 30 other classes (runtime default L3, `authority.rs:37-45`). 4.1.3 `TOOL_POLICY` lacks the `plugins` governance
  block and `EXEC_PLUGIN`. 4.1.4 `POLICY_PRECEDENCE` lacks the three `TOOL_POLICY.plugins.*` rules added with the V-H1
  repair.
- **D** the pack's justification for admitting legacy kernels (`11` Phase 1.3: defects “lie in the binaries' install and
  use logic, not in kernel content”) is **false** on the diffs above.

**Failure scenario.** A collaborator (A2) on a project installed from signed 4.1.6 commits the genuine 4.1.2 kernel and
a 1.1.0 lock, and deletes `governance/trust/`. Every clone: tree digest equals a legacy entry → `AUTHENTICATED_REJECTED`,
`verified:true`, floors from 4.1.2 → L3 agents lift freezes and pass update authority. Doctor reports HIGH, not CRITICAL,
so post-update verification does not roll back. The same works with any older **signed** release after a later release
strengthened a floor, and needs no Git when A3 restores an older set through adoption batch rollback (RV-M1) or a forged
journal with the lock (`05` §6).

**Correction.** CD-1. **Acceptance.** AC-C1…C6; RV-A15, A18, A19, A27.

---

## RV-H2 — HIGH — Lifecycle facts are not replay- or omission-safe (stale CERTIFIED, omitted REJECTED/WITHDRAWN, stripped revocation)

**Statement.**
- V13 takes the highest certification sequence *among the statements presented* (bundle, embedded, `governance/trust/`).
- Negative states (`REJECTED`, `WITHDRAWN`) live only in optional certification statements, with no floor or high-water.
- OP-3 relaxes gates on CERTIFIED and gates on REJECTED.
- Revocations and newer root versions delivered after the binary ships are accepted in whatever subset is present. Their
  high-water marks live in an A2-writable lock and an A3/A4-selectable user store (`05` §5).
- The threat model calls the residual an “offline freeze” (`01` §5, RK-02). That understates it: the metadata is
  actively removable.

**Evidence.** **D** `04` V4/V13, `05` §5–§7, `07` §4, `00` §5 OP-3. The E2 probe (reproduced in
`evidence/E1-E5-reproduction-output.txt`) shows the consequence class: gate skipped, applied without `--approve`.

**Failure scenarios.**
1. **Stale certification (A1).** 4.1.7 was CERTIFIED (seq 1), later WITHDRAWN (seq 2). A mirror serves the genuine
   bundle with only seq 1 → V13 → CERTIFIED → `update --apply` with no gate on every consumer whose binary predates seq 2.
2. **Omitted rejection (A1).** A genuinely signed rejected candidate served without its REJECTED statement → V13 finds
   nothing → `AUTHENTICATED_UNCERTIFIED` → `init` proceeds ungated (OP-3).
3. **Revocation stripping (A2/A4).** After revoking release R, or rotating out key K in root N+1, A2 deletes
   `governance/trust/revocations.dsse.json` and `root/N+1.json`. Any fresh clone, CI job or machine with a redirected
   `XDG_CONFIG_HOME` evaluates with the compiled floor only → R, or a K-signed malicious statement, verifies.

**Why HIGH.** Scenario 1 is E2 again: an authorisation relaxation derived from data the requester selects. Scenario 3
means compromise recovery (`05` §7) is durable only through binary upgrade, which the pack does not state.

**Correction.** CD-2. **Acceptance.** AC-D1…D5; RV-A10, A17, A21, A22, A23, A24.

---

## RV-H3 — HIGH — Verified bytes are not the bytes enforced (use-time TOCTOU)

**Statement.** RoT-1 specifies a `TrustedKernel` “over installed dir” (`04` §2) with one verification per process
(`04` §5) and no rule binding later reads to the digested bytes. Installed-tree rules for symlinks and ancestors at use
time are unspecified. RT-22 covers only source-side races.

**Evidence.** **E** `evidence/R2b-use-time-toctou.{py,json}` against the 4.1.5 binary, which has the same verify-then-reread
shape (`kernel_trust.rs:134` then `policy.rs:98-101`):

| Run | `spec/decisions/D-9001.yaml`, `product/restricted-plan.md` (classified `restricted`) |
|---|---|
| control, intact kernel | excluded `sensitivity:restricted`; not retrievable |
| raced `rebuild-memory` (swap 0.11 ms after kernel_trust's read; bytes restored on exit) | **indexed** with `sensitivity = restricted` |
| afterwards, unraced | `memory query` returns **both**; `kernel trust` `verified:true`; doctor D003/D004/D029 ok; policy bytes identical to the release |

A preliminary run (`evidence/R2-preliminary-probes.py`) consumed the swapped floor in 5/5 trials.

**Failure scenario.** Any same-user process running during a `gov` command (a compromised dependency, tool or plugin; A3
in the pack's own model, as in E3/E5) removes a constitutional floor for that command. It leaves persistent harm
(restricted content in the derived index) and no evidence: every integrity attestation stays green.

**Correction.** CD-4. **Acceptance.** AC-E1…E3; RV-A14, A25, A37, A38.

---

## RV-H4 — HIGH — A non-release role can confer kernel authenticity (legacy identity signed by the certification role)

**Statement.** The legacy-identity statement is signed by the **certification** role (threshold 1; custody “release owner
/ product owner”, no hardware requirement) (`05` §1; `11` Phase 1.2). It makes an installed kernel
`AUTHENTICATED_REJECTED`, `verified:true`, with floors read from that kernel (`08` §5; `06` §6). Its payloadType sits in
the general envelope allowlist (`schemas/dsse-envelope.schema.json`) with a role binding (`05` §1). The pack never states
that legacy identity is accepted **only** from the copy compiled into the binary (`08` §5 says “compiled”; `05` §2
places it in `trust/production/`; nothing forbids bundle or `governance/trust/` copies).

**Failure scenario.** A certification-key thief signs a legacy-identity payload naming the tree digest of a malicious
kernel (e.g. `never_index_classes: [secret]`) as version 4.1.5, and ships it beside that kernel in a bundle or commit →
authenticated policy root. The pack's own invariant “certification … may never sign release statements” is broken in
substance: this statement *is* a release-authenticity statement.

**Correction.** CD-3. **Acceptance.** AC-H4; RV-A20.

---

## MEDIUM

| ID | Finding | Evidence | Correction | Acceptance |
|---|---|---|---|---|
| **RV-M1** | **Writers are not path-guarded; the ingress map omits four writers or deciders.** Adoption batch rollback restores arbitrary paths, including kernel and lock, from `.governance-runtime/migration/batch-N/` (`migrations/executor.rs:9-13, 304-350`; reachable from `gov adopt rollback` and `gov recover`). CIT `write_file` guards only `governance/kernel/**` (`cit/mod.rs:704`); `move_file` (`:713`) and `delete_file` (`:731`) have no governance guard. A7/A11 still decide on `verify_kernel` against a self-manifest (`adopt.rs:816, 1363`). Adapter freshness uses lock hashes (`adapters.rs:168`). Completeness enforcement by symbol grep (`02` §3, `04` §4.6) cannot see computed-path writes. `02` I-10 calls `recover` “project state only”, which is incorrect. | C | CD-5 | AC-G1…G4; RV-A16, A27, A28 |
| **RV-M2** | **Partial-install fail-open is unspecified.** In 4.1.5 a missing `KERNEL_MANIFEST.json` or lock ⇒ `uninstalled` with `policy_root = governance/kernel`, and `guard` passes (`kernel_trust.rs:128-130, 289-291`). `doctor` and `capabilities` open projects without the install requirement (`cli/src/main.rs:743, 865`). RoT-1 defines `installed` as “a kernel and lock are present” but no policy root or guard for partial states, including the mid-swap window. | C | CD-6 | AC-E3; RV-A26 |
| **RV-M3** | **Install authority is read from the material being installed.** First install takes AUTHORITY_POLICY “from the authenticated target release” (`09` §1 step 2); today `init.rs:246` checks authority after installing. A genuinely signed older or dev target with weaker authority authorises its own installation. | D, C | CD-7 | AC-H1; RV-A29, A30 |
| **RV-M4** | **Pre-RoT-1 binaries keep circular trust on RoT-1 projects.** Lock 2.0.0 keeps `kernel_manifest_hash`/`release_hash` (`08` §3; `13` row 4), so a 4.1.5 binary's V-H2 check (`kernel_trust.rs:156-169`) passes an E4-style replacement. Omitting those fields makes 4.1.5 fail closed (`lock_hash.is_empty()` ⇒ not verified). | C | CD-8 | AC-H2; RV-A31 |
| **RV-M5** | **Verification acceptance and candidate status are not mechanically distinct.** The verifier holds no key; `verdict.digest` is descriptive and unchecked; OP-4 gives candidates no signed stage, so every signed candidate is a permanent production-installable release unless revoked. | D | CD-9 | AC-D3 |
| **RV-M6** | **Bootstrap anchoring is weaker than the threat model assumes.** Publication channels (a) and (b) are hosted with the releases (`06` §2.1). OP-6's default makes TA-5 false for automated installs. Lineage mismatch on an existing project has no specified failure. A fork binary is `trust_profile: production` under another lineage. | D | CD-10 | AC-A3, AC-H5; RV-A34, A35 |
| **RV-M7** | **Reference-profile use-time integrity relies on plugin-reported digests (T6) and size/mtime gating (A3-controllable); the runtime environment is not re-verified at use.** Contradicts D-0007/D-0008 rule (2). | D | CD-11 | AC-H6; RV-A32 |
| **RV-M8** | **A signed migration can remove project-owned strengthening without a gate, and the migration chain may fork.** Gates trigger only on signer-declared `breaking`/`human_gates`. Overlay preservation accepts any migration-declared change (`update.rs:235-242`; `migrations/framework.rs:124-170`). `path()` takes the first `from_version` match (`migrations/framework.rs:36-58`). | C, D | CD-12 | AC-B2, AC-H7; RV-A04, A05 |

## LOW

| ID | Finding | Correction |
|---|---|---|
| **RV-L1** | Specification inconsistencies: `update_impact` “verified at V15” (no V15); RT-05(c) expects `RELEASE_THRESHOLD_NOT_MET` for empty `signatures` while the envelope schema has `minItems: 1`; tree rules allow NFC Unicode paths while GOV-JCS-1 requires ASCII member names; `release_id` wording `tree_digest[0:16]` includes the `sha256:` prefix; migration `breaking`/`human_gate` duplicated in statement and file without an equality rule; key id not recomputed and duplicate public keys not refused; algorithm-migration role policy not representable in the trust-root schema; OP-5 “overlay may make it gating” contradicts “no security decision uses signer-supplied time”; revocation and certification matching fields (`release_id`/`version` vs digest) unspecified; fail-closed behaviour for a corrupt compiled root unspecified. | CD-13 |
| **RV-L2** | Test trust profile as a cargo feature on the shared `gov-runtime` crate is exposed to feature unification in workspace builds that include test targets. | CD-13 |
| **RV-L3** | Reproducibility and immutability details: the statement needs deterministic `released_at`/`provenance.builder` inputs for sign-what-you-reproduced (`release.rs` stamps `now_iso()` today); key rule 3.1 (“machines holding a canonical clone”) conflicts with the signing host reproducing from the repository; the append-only file set of `release/releases/<v>/` after build is undefined; the architecture commit `676dfce` sits on the rejected `release/4.1.5-rc1` branch (tag `v4.1.5-rc1` still at `da9c851`, so immutability holds). | CD-13 |
| **RV-L4** | `status: PROVISIONAL` for D-0008/ARCH-0002 is treated as active by `RecordStore::active()` (`records.rs:478-482`) and the context compiler (`context/mod.rs:52, 89`). No effect in the uninstalled canonical repository, and exceptions require ACTIVE (`exceptions.rs:182-185`), but the pattern leaks into any governed project. | CD-13 |
