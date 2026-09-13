# Output 13 — Legacy-version compatibility model

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 2 replaces the rev 1 compatibility table with a model for every legacy artefact. It addresses RV-M4 (CD-8) and
> the legacy parts of RV-H1 and RV-H4.

## 1. Legacy artefacts in scope

| Artefact | Revision 2 treatment | Section |
|---|---|---|
| Kernels of releases 4.1.2–4.1.5 | recognised by a compiled registry; never eligible | §2 |
| Pre-RoT binaries (4.1.2–4.1.5) opening RoT-1 projects | explicit trust-format boundary; fail closed | §3 |
| Future trust formats | readers refuse unknown formats | §4 |
| Lock 1.1.0 projects under a RoT-1 binary | `PARTIAL`, read-only, update to an eligible release | §5 |
| Snapshots made by 4.1.5 | historical identities → refused as restore targets | §6 |
| Environment variables and CLI behaviour | removals and restrictions | §7 |
| Prior independent harnesses and the review's evidence | expected results by binary profile | §8 |
| Revision-1 statement formats | never issued; not accepted | §9 |

## 2. Historical kernels (4.1.2–4.1.5)

- **Recognition.** A historical-identity registry lists version, release id, release commit, tree digest, manifest digest,
  status (`REJECTED`) and verifier report digest for each release. It is signed under `release-final` and compiled into
  the binary; it is accepted from **no other source** (`05` §2, SV-2). Digests were independently reproduced
  (`../4.1.6-review/evidence/continuity-check-4.1.2-4.1.5.txt`): tree digests equal the published `release_hash` values
  `9964830b…` (4.1.2), `6bebfdbb…` (4.1.3), `e5e2f2c7…` (4.1.4), `962f9848…` (4.1.5).
- **Status.** `HISTORICAL_IDENTIFIED`, `INELIGIBLE(historical)` in production, always (`19` §6 E1, §7). Recognition lets
  a RoT-1 binary report exactly which legacy release is installed and refuse it; it grants nothing.
- **Why never eligible.** Legacy kernel content is not security-equivalent to current releases:
  - 4.1.2 `AUTHORITY_POLICY` lacks `update_apply` and `resume_control`, which the 4.1.5 runtime defaults to L3 instead of
    L4. The review showed an L3 role passing both on the genuine 4.1.2 kernel
    (`../4.1.6-review/evidence/R1-legacy-kernel-floors.json`).
  - 4.1.3 `TOOL_POLICY` lacks the plugin governance block.
  - 4.1.4 `POLICY_PRECEDENCE` lacks the plugin-registry rules added with the V-H1 repair
    (`../4.1.6-review/evidence/legacy-kernel-security-diffs.txt`).
- **Consumer consequence.** A project installed by 4.1.2–4.1.5, opened by a RoT-1 binary, is read-only until updated to
  an eligible signed release. Floors come from the EmbeddedSnapshot ⊔ TPS in the meantime. This is intentional: every
  legacy release is REJECTED.
- **Test profile.** `gov-test-profile` treats historical identities as labelled test material so the prior harnesses can
  still exercise legacy-to-current upgrade logic (§8).

## 3. Trust-format boundary for pre-RoT binaries

### 3.1 Design

A RoT-1 installation writes three markers that every pre-RoT binary reads in a way that cannot result in “verified”:

| Marker | Content | Effect on pre-RoT binaries |
|---|---|---|
| `framework.lock` `kernel_manifest_hash` and `release_hash` | the sentinel `ROT-1-TRUST-FORMAT:requires-gov>=4.1.6:this-binary-cannot-verify-this-project` | 4.1.5 `kernel_trust` compares its manifest hash with this string → mismatch → not verified. The problem message quotes the sentinel, so the refusal text tells the operator which binary is required. |
| `governance/kernel/KERNEL_MANIFEST.json` (tombstone) | `trust_format: rot-1`, `notice: <sentinel>`, `payload_hash: <sentinel>`, and a `files` map containing only the non-existent entry `TRUST-FORMAT-ROT-1/requires-gov-4.1.6` | every 4.1.x `verify_kernel` reports that entry missing and every real file added → payload not intact. 4.1.2, 4.1.3 and 4.1.4 have `verify_kernel` and doctor D003, checked in their sources at `8ad06be`, `26ab5b6`, `47d8394`. |
| `governance/trust/FORMAT` | `{"minimum_reader":"4.1.6","trust_format":"rot-1"}` | ignored by pre-RoT binaries; read first by RoT-1 binaries (§4) |

RoT-1 binaries never read the sentinel fields or the tombstone. Identity lives in `kernel.*`, `release_statement_digest`
and the trust record (`08` §3).

### 3.2 Executed feasibility evidence against the real 4.1.5 binary

Script and output: `evidence/F1-format-boundary-probe.py`, `evidence/F1-format-boundary-probe.json` (scratch consumer; the
genuine 4.1.5 payload rewritten into the rev 2 format).

| 4.1.5 command | Observed |
|---|---|
| `kernel trust` | `verified: false`; embedded baseline substituted; problems text contains the sentinel |
| `kernel verify` | `ok: false` |
| `doctor` | `UNHEALTHY`; failed critical D003, D004, D029 |
| `task create` (governed mutation) | refused `KERNEL_TAMPERED`; message contains the sentinel |
| `rebuild-memory` | refused `KERNEL_TAMPERED` |
| `status`, `capabilities plugins` (read-only) | run, with 4.1.5's own substituted baseline |
| `kernel reinstall` (4.1.5's exempt remedy) | refused `KERNEL_MISMATCH`, **after** overwriting the kernel directory and tombstone |

Conclusion: 4.1.5 fails closed and names the required binary. It never interprets a RoT-1 project as verified.

### 3.3 Residuals of the boundary (explicit)

| ID | Residual | Bound |
|---|---|---|
| LC-1 | An operator running 4.1.5 `kernel reinstall`, `update --apply` or `init --force` on a RoT-1 project can overwrite the kernel directory with 4.1.5 content before 4.1.5 refuses or completes. | The next RoT-1 process reports `KERNEL_TAMPERED` or `INSTALL_STATE_PARTIAL` and never trusts the result; the remedy is `gov kernel reinstall` with a RoT-1 binary. Availability impact only. |
| LC-2 | 4.1.2–4.1.4 binaries read constitutional floors from installed files without any trust boundary (their own V-H2 defect). On a RoT-1 project they report the kernel as not intact (D003) but still operate. | These binaries are REJECTED releases. RoT-1 cannot change their behaviour through data. The release protocol lists them as unsupported, and an `artifact-final` revocation entry names them. |
| LC-3 | 4.1.5 read-only commands run with 4.1.5's own embedded baseline, which 4.1.5 reads from a mutable cache (review E3). | Read-only; 4.1.5's own defect; mutations refused. |

## 4. Future format evolution

- `governance/trust/FORMAT` is read before anything else (`18` §9). A binary that does not implement the named
  `trust_format`, or whose version is below `minimum_reader`, stops with `TRUST_FORMAT_UNSUPPORTED`. It never falls back
  to an older interpretation (D-0008 rule 12).
- A future format (`rot-2`) keeps the same markers: new sentinel text, and the tombstone manifest naming the new minimum.
  Every older RoT-1 binary then fails closed by the same rule.
- Format changes are install transactions (update), never in-place edits.

## 5. Lock 1.1.0 projects

| Consumer state (opened by a RoT-1 binary) | Verdict | Allowed | Path forward |
|---|---|---|---|
| lock 1.1.0, kernel equals a historical digest | `PARTIAL` + `HISTORICAL_IDENTIFIED`, `INELIGIBLE(historical)` | read-only; remedies | `gov update --apply --source <signed eligible release>` (gate; authority from floor) → lock 2.0.0 + trust record |
| lock 1.1.0, kernel matches no known identity | `PARTIAL` | read-only; remedies | same |
| lock 2.0.0, eligible final | normal | all | — |
| lock 2.0.0, format unknown to this binary | `FORMAT_UNSUPPORTED` | `gov version`, `gov doctor` | upgrade `gov` |

## 6. Snapshots and rollback targets from 4.1.5

Snapshots under `.governance-runtime/update/<version>/` made by 4.1.5 carry legacy kernels. Restore evaluates them like
any source (`20` §3): they are historical identities → `SNAPSHOT_INELIGIBLE(historical)`. Rolling back from 4.1.6 to
4.1.5 is therefore refused. Revision 1's migration plan offered that path; it is removed because 4.1.5 is REJECTED and
its kernel is below the floor. Recovery from a defective 4.1.6 is a newer eligible release or `kernel reinstall` of 4.1.6.

## 7. Environment variables and CLI changes

| Item | Revision 2 |
|---|---|
| `GOV_KERNEL_SOURCE` | removed |
| `GOV_KERNEL_CACHE` | removed; no cache on any trust path (`18` §7) |
| `GOV_CANONICAL_ROOT` | source selection only; never a schema, scanner-policy or trust input |
| `HOME`, `XDG_*` | never select the Verifier Trust Store or pin files (`17` §4, `06` §3) |
| `gov kernel reinstall --source <arbitrary>` | must authenticate to the installed statement digest; never follows `lock.source` as a path |
| `gov update` refusals for trust reasons | `ok: false` with typed codes (API-0002 exit 1); gate-pending responses keep the 4.1.5 shape |
| `gov update --rollback` to a legacy snapshot | refused (§6) |
| New commands | `gov trust show`, `confirm-root`, `adopt-lineage`, `refresh --from`, `export`, `publish` (producer), `verify-artifact`; `gov release attach-signature`, `promote`; `gov kernel export` |

## 8. Prior harnesses and review evidence — expected results

The four prior harnesses run **unchanged**, with `GOV_CANONICAL_ROOT` pointing at a clone of the 4.1.6 final tag that
contains signed statements.

| Harness | `gov` (production profile) | `gov-test-profile` |
|---|---|---|
| `release/verification/4.1.2/heldout/harness.py` | as 4.1.5 (36/1/1), **except HV-11**, which installs a synthetic unsigned `prev-4.1.1`: expected `UNSIGNED_SOURCE_REFUSED`. Classified as an intended trust refusal; INV-008 re-proven by RT-11/RT-30. | 36/1/1 |
| `release/verification/4.1.3/heldout-new/harness_v2.py` | Scenarios that install or update to historical releases (NV-03, NV-08, NV-13; consumers from the 4.1.2 worktree) are refused `RELEASE_INELIGIBLE(historical)`. Classified as intended refusals and re-proven with signed test-profile equivalents. NV-09 and NV-19 remain frozen to 4.1.3. | 13/2 |
| `release/verification/4.1.4/heldout-v3/harness_v3.py` | 14/2 (VV-05, VV-07 frozen to the 4.1.4 identity); any scenario installing a historical release classified as above | 14/2 |
| `release/verification/4.1.5/heldout-wv/harness_wv.py` | 6/0, with historical-install steps classified as above | 6/0 |
| Review `R1-legacy-kernel-floors.py` (pointed at 4.1.6) | **must flip**: L3 `update --apply` and `resume` refused on the 4.1.2 kernel | — |
| Review `R2b-use-time-toctou.py` (pointed at 4.1.6) | **must flip**: restricted records excluded and not retrievable in 20/20 trials | — |
| Escalation `probe.sh` E1–E5 (pointed at 4.1.6) | every probe refused or not verified; restricted floor intact | — |
| `F1-format-boundary-probe.py` | unchanged expectation for the 4.1.5 binary; with `GOV` pointed at 4.1.6, the same project is `verified` only when genuinely installed | — |

Any other change is a regression unless the verifier independently classifies it as an intended refusal of an
unauthenticated or ineligible path and re-proves the original property with a signed equivalent.

## 9. Revision-1 statement formats

Revision-1 payloadTypes (`release-statement.v1`, `certification-statement.v1`, `revocation-statement.v1`,
`legacy-identity.v1`, `artifact-statement.v1`, `profile-statement.v1`, `trust-root.v1`) were never issued. No
revision-2 binary accepts them (`05` §2).

## 10. Other compatibility consequences

| Area | Change | Mitigation |
|---|---|---|
| Unsigned sources | refused on production (`UNSIGNED_SOURCE_REFUSED`) | `gov-test-profile`; `--allow-unsigned-development` (labelled, never eligible) |
| Every production install and update | Human Decision Gate bound to the statement digest (OP-3 mode A) | automation answers gates through the existing gate channel; mode B is owner-optional |
| First use of a lineage on a machine | `TRUST_ROOT_UNCONFIRMED` until confirmation (OP-6 mode a) | pin file or `--confirm-trust-root` for CI |
| `framework.lock` | 2.0.0: identity fields renamed, sentinels in 1.1.0 names | tools read `kernel.*` |
| New protected directories | `governance/trust/`, `governance/.tx/` | small signed files; documented in the consumer contract |
| `gov kernel trust` output | multi-axis verdict (`19` §6); `verified` also requires eligibility | unchanged for eligible installs |
| CIT manifests and adoption plans | protected paths refused at planning | no legitimate CIT writes these paths |
| Dependencies | one pure-Rust Ed25519 crate; platform secure-open primitives | D-0002 single binary preserved |
| Platforms | production profile needs the `18` §3 primitives | `TRUST_PLATFORM_UNSUPPORTED` elsewhere |
| Performance | one signature check per statement; kernel read into memory once per process (~1 MiB today) | no cross-process cache |
| Records | D-0007 superseded only on approval of D-0008 | D-0008 restates D-0007 rules (1)–(4) |
