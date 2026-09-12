# Governance OS 4.1.5 Framework Update/Migration/Rollback Chain Verification Report

**Executor**: Independent test executor (Claude Opus 4.6, fresh session)
**Date**: 2026-09-12
**Candidate**: v4.1.5-rc1 (commit da9c851)
**Binaries**: clone412 (4.1.2, commit 8ad06be), clone414 (4.1.4, tag v4.1.4-rc1), clone415 (4.1.5, tag v4.1.5-rc1)

---

## Summary Table

| Step | Description | Verdict | Key Observations |
|------|-------------|---------|------------------|
| 1 | 4.1.2 consumer creation | PASS | init ok, rebuild-memory ok, overlay + spec records committed |
| 2 | Update chain 4.1.2->4.1.3->4.1.4->4.1.5 | PASS | All hops gated independently, kernel trust verified at each, overlay preserved |
| 3 | Direct multi-hop 4.1.2->4.1.5 | PASS | 3 migrations applied in sequence, single gate, overlay change declared |
| 4 | Machine B rebuild | PASS | manifest_hash identical across machines |
| 5 | Rollback chain 4.1.5->4.1.4->4.1.3->4.1.2 | PASS | Overlay byte-identical, ledger entries appended, further rollback refused (SNAPSHOT_MISSING) |
| 6 | 4.1.4 consumer with plugin/exception | PASS | Plugin survives update+rollback, invalid exception correctly refused |
| 7 | Release payload integrity | PASS | Migrations byte-identical, overlay-templates identical, all 4 releases verify clean |
| 8 | Update-source authenticity | **FAIL** | Tampered payload accepted; kernel trust reports verified after tampering |

---

## Step 1: Genuine 4.1.2 Consumer

- Created from greenfield fixture, `git init`, `gov init` with 4.1.2 binary
- `rebuild-memory`: 151 artifacts indexed, manifest_hash `0976da51...`
- Added overlay customisation (`CHANGE_POLICY.semantic_candidates_by_radius.R1: 5`) and spec record `D-TEST-001`
- framework.lock: version `4.1.2`, release_hash `9964830b...`, lock_schema_version `1.0.0`
- **Evidence**: `step1_init.json`, `step1_rebuild.json`, `step1_hashes_412.txt`

## Step 2: Update Chain 4.1.2 -> 4.1.3 -> 4.1.4 -> 4.1.5

### 4.1.2 -> 4.1.3
- `update --apply` without approval: refused with `HUMAN_GATE_REQUIRED`, gate `HDG-0001` created
- `update --apply --approve` before presenting/answering gate: refused with `"applied": false, "reason": "human gate not presented/answered (INV-008)"`
- After `gate present HDG-0001` + `decide HDG-0001 --option A`: update applied
- Migration: `M-4.1.2-4.1.3` (note, set_lock_field, require_index_rebuild, regenerate_adapters)
- Overlay change: `reconciled:REPOSITORY_CONTRACT.yaml.paths[pattern=governance/tests/**].lexical_index`
- Lock: version `4.1.3`, release_commit `78f68538...`, source `release:agentic-engineering-os@4.1.3`, lock_schema_version `1.0.0`
- Kernel trust: `"verified": true`
- D-TEST-001 spec record: preserved (hash unchanged)

### 4.1.3 -> 4.1.4
- New gate `HDG-0002` raised (prior HDG-0001 did NOT authorize this hop)
- Migration: `M-4.1.3-4.1.4` (note, set_overlay_rule skipped:already_set, set_lock_field, require_index_rebuild, regenerate_adapters)
- No overlay changes (set_overlay_rule skipped because already reconciled in 4.1.3 hop)
- Lock: version `4.1.4`, release_commit `c6b594ba...`, source `release:agentic-engineering-os@4.1.4`, lock_schema_version `1.1.0`
- Kernel trust: `"verified": true`

### 4.1.4 -> 4.1.5
- New gate `HDG-0003` raised
- Migration: `M-4.1.4-4.1.5` (2 notes, set_lock_field, require_index_rebuild, regenerate_adapters)
- No overlay changes
- Lock: version `4.1.5`, release_commit `25dac6ef...`, source `release:agentic-engineering-os@4.1.5`, kernel_manifest_hash `b3086404...`, lock_schema_version `1.1.0`
- Kernel trust: `"verified": true`, fingerprint `a71e7f22...`
- Doctor verdict: DEGRADED (D021 obsolete audit, D022 cargo gap -- both non-critical)
- All overlay hashes identical across 4.1.3/4.1.4/4.1.5 (except REPOSITORY_CONTRACT changed at 4.1.3)

**Evidence**: `step2_*.json`, `step2_hashes_*.txt`, `step2_lock_*.txt`

## Step 3: Direct Multi-Hop 4.1.2 -> 4.1.5

- `update --check` reports: `migration_path: ["M-4.1.2-4.1.3", "M-4.1.3-4.1.4", "M-4.1.4-4.1.5"]`, `migration_path_complete: true`
- Single gate `HDG-0001` for the entire chain
- All 14 operations applied in order (4 per migration, M-4.1.3-4.1.4 has 5 including set_overlay_rule)
- `overlay_keys_changed: ["REPOSITORY_CONTRACT.yaml:paths[pattern=\"governance/tests/**\"].lexical_index"]`
- Impact radius: `R4` (vs `R3` for single hops)

**Evidence**: `step3_*.json`

## Step 4: Machine B Rebuild

- `rebuild-memory`: manifest_hash `ea1fdef0...` on both machines (IDENTICAL)
- `policy overrides`: 1 applied (semantic_candidates_by_radius.R1 = 5, mode overridable), 0 refused
- Kernel trust: verified, version 4.1.5
- Doctor: DEGRADED (same non-critical issues)

**Evidence**: `step4_*.json`

## Step 5: Rollback Chain 4.1.5 -> 4.1.4 -> 4.1.3 -> 4.1.2

### Rollback 4.1.5 -> 4.1.4
- `"rolled_back_to": "4.1.4"`, kernel_ok, doctor DEGRADED
- Overlay hashes: byte-identical to pre-4.1.5 state
- Ledger entry appended to `spec/reports/framework-updates.jsonl`
- Kernel trust: verified, version 4.1.4

### Rollback 4.1.4 -> 4.1.3
- Kernel trust: verified, version 4.1.3
- Ledger entry appended

### Rollback 4.1.3 -> 4.1.2
- REPOSITORY_CONTRACT.yaml hash returned to original 4.1.2 value (`6f4bd4e5...`)
- All overlay hashes match baseline
- Kernel trust: verified, version 4.1.2
- Ledger entry appended

### Further rollback (must fail)
- `"code": "SNAPSHOT_MISSING"`, `"message": "no unconsumed update snapshot..."`

### Re-apply check
- `update --check --source 4.1.2`: `"up_to_date": true`

### Downgrade check
- `update --check --source 4.1.2` from 4.1.3: `"downgrade": true, "compatible": false`

### Ledger
- 7 entries in `spec/reports/framework-updates.jsonl` (1 auto-rollback, 3 updates, 3 manual rollbacks)

**Evidence**: `step5_*.json`, `step5_ledger.jsonl`

## Step 6: 4.1.4 Consumer with Plugin/Exception/Overlay

### Setup
- Created with 4.1.4 binary, added:
  - Plugin descriptor: `governance/project/plugins/test-echo.yaml` (code_intel capability, shell script)
  - Exception: `EXC-0001` (MEMORY_POLICY.freshness.on_stale_close -> degrade, citing D-EXC-001)
  - Overlay customisation: `CHANGE_POLICY.semantic_candidates_by_radius.R2: 8`
- Doctor at 4.1.4: UNHEALTHY (D027 refuses EXC-0001 because key is immutable)

### Update to 4.1.5
- First attempt with exception present: update applied but auto-rolled-back (VERIFICATION_FAILED / D027)
  - D027 message: `"exception EXC-0001 references D-EXC-001 (spec/decisions/D-EXC-001.yaml), which is a '' record, not a decision"`
  - This is 4.1.5 validating exception decisions more strictly: the decision record did not have `authorises_exceptions` / `permits_policy_keys`
- After removing invalid exception: update succeeded
- Plugin: still listed as usable by `plugins list`, descriptor preserved
- Doctor: DEGRADED (D021 + D022 only)
- Policy overrides: 1 applied (R2=8), 0 refused

### Rollback to 4.1.4
- Overlay restored, plugin descriptor preserved
- Note: PROJECT_EXCEPTIONS.yaml hash changed from initial because it was modified before update

**Evidence**: `step6_*.json`, `step6_hashes_414.txt`

## Step 7: Release Payload Integrity

### Migration file comparison
- All shared migrations (M-4.1.1-4.1.2, M-4.1.2-4.1.3, M-4.1.3-4.1.4, README.md) are byte-identical between 4.1.4 and 4.1.5 payloads
- M-4.1.4-4.1.5.yaml is only in the 4.1.5 payload (expected)

### Overlay template comparison
- All 7 overlay templates are byte-identical between 4.1.4 and 4.1.5 payloads
- M-4.1.4-4.1.5.yaml declares `overlay_template_changes: []` (consistent)

### Release verify
| Release | ok | modified | missing | added | release_hash_matches_kernel | certification |
|---------|------|----------|---------|-------|---------------------------|---------------|
| 4.1.2 | true | [] | [] | [] | true | REJECTED |
| 4.1.3 | true | [] | [] | [] | true | REJECTED |
| 4.1.4 | true | [] | [] | [] | true | REJECTED |
| 4.1.5 | true | [] | [] | [] | true | READY_FOR_INDEPENDENT_REVERIFICATION |

**Evidence**: `step7_release_verify_*.json`

## Step 8: Update-Source Authenticity

### Test: Weakened SECURITY_POLICY
- Copied 4.1.5 release payload to scratch dir
- Modified `SECURITY_POLICY.yaml`: removed `restricted` from `never_index_classes` (was `[secret, restricted]`, now `[secret]`)
- Did NOT update KERNEL_MANIFEST.json or manifest.json

### Result: **FAIL -- tampered payload accepted**
- `update --apply --approve` with tampered source: `"applied": true`
- Installed SECURITY_POLICY: `never_index_classes: [secret]` (tampered)
- `kernel trust`: `"verified": true`
- `doctor D003/D004/D029`: all `ok: true`
- The update process regenerated KERNEL_MANIFEST.json and framework.lock from the installed (tampered) files
- `release verify` on the tampered source dir correctly reports `"ok": false, "modified": ["policies/SECURITY_POLICY.yaml"]`

### Analysis
- `release verify` (pre-install check) detects the tampering, but `update --apply` does NOT call `release verify` on the incoming payload before installation
- The kernel trust boundary (V-H2) verifies the installed kernel against its own KERNEL_MANIFEST.json and framework.lock, but since both are derived from the installed content, a consistently tampered payload passes
- The `manifest.json` (outside kernel/) contains `file_hashes` that would detect the tampering, but this is not checked during update
- Payload fingerprints differ: legitimate `a71e7f22...` vs tampered `dad9f565...`

### Anomaly
This means `gov update --apply` does not enforce source-payload integrity. An attacker who can supply a tampered release directory (with modified kernel files but unchanged KERNEL_MANIFEST.json) can install weakened policies that pass all post-install verification. The `release verify` command exists but is not integrated into the update pathway.

**Evidence**: `step8_*.json`, `step8_kernel_trust_tampered.json`, `step8_release_verify_tampered.json`

---

## Anomalies

1. **CRITICAL: Update pathway does not verify source payload integrity (Step 8)**
   - `gov update --apply` installs kernel files from the source directory without checking them against the source's manifest.json `file_hashes` or KERNEL_MANIFEST.json
   - A tampered SECURITY_POLICY with `restricted` removed from `never_index_classes` was installed and passed all post-install checks (`kernel trust`, `doctor D003/D004/D029`)
   - `release verify` would detect this but is not called during update
   - The KERNEL_MANIFEST.json is regenerated after install, making the tampering self-consistent

2. **First update attempt with immutable-override was auto-rolled back (Step 2, first 4.1.2->4.1.3 attempt)**
   - Correct behavior: the CHECKPOINT_POLICY override was correctly refused by D027, and the update was auto-rolled back
   - This demonstrates that post-install doctor verification with critical check enforcement works

3. **4.1.5 exception validation is stricter (Step 6)**
   - A `PROJECT_EXCEPTIONS` entry referencing a decision record that lacks `authorises_exceptions` / `permits_policy_keys` is refused
   - The error message says the record is "a '' record, not a decision" -- the classification of the hand-written YAML was unclear

4. **Gate scoping is per-hop (Step 2)**
   - Gate HDG-0001 (4.1.2->4.1.3) does NOT authorize the 4.1.3->4.1.4 hop -- a new HDG-0002 was raised
   - This is correct: each update hop requires its own gate

5. **Multi-hop uses a single gate (Step 3)**
   - Direct 4.1.2->4.1.5 update uses a single gate for all 3 hops -- this is acceptable since the impact is presented as a composite

6. **Note on consumer3 rollback overlay identity**
   - PROJECT_EXCEPTIONS.yaml hash changed between the initial 4.1.4 state and after rollback because the exception was removed before the update; the snapshot captured the modified state
