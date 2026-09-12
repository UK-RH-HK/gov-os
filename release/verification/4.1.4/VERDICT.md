# Independent re-verification verdict — repair candidate 4.1.4

Candidate verified: commit `47d8394b945bcfd9f35a5fee80836e424a4570dc` (branch `release/4.1.4-rc1`, tag `v4.1.4-rc1`,
payload `release/releases/4.1.4`, release_hash `e5e2f2c79329004019c146b90787eeaebbb49f929765c5a7e37991de00437d2b`).

**Verdict: OS_RELEASE_CANDIDATE_REJECTED** (repairable — see `INDEPENDENT_REVERIFICATION_REPORT.md` §11–§13).

## What the repair achieved

- **C-N1 repaired** — CIT approval and execution derive only from a presented, answered-A gate with an ACTIVE derived
  decision, re-checked at execution time. Nine independent attacks (unpresented, presented-unanswered, declined,
  revoked-after-approval, tampered answer, forged approval object, cross-CIT gate, agent answer claimed as human,
  under-authority approve/answer) were all refused with specific codes and nothing was written (VV-01 PASS).
- **H-N1 repaired** — 15 simultaneous weakening overrides (authority levels, never-index/never-export/secret patterns,
  auto-approve radius, snapshot-before-execute, gate presentation, plugin min_authority, test-status widening,
  archive mutation, and `POLICY_PRECEDENCE.default_mode` itself) were all refused, the effective policy was unchanged,
  an L0 role was denied, restricted content stayed excluded, and doctor D027 reported CRITICAL (VV-02 PASS).
- **H-N2 partially repaired** — schema validation, content pinning, drift detection, health checks, the
  elevated-permission registration gate, registration authority and `capabilities invoke` authority all hold. The
  authority floor does not (see below).
- Every MEDIUM/LOW item of the 4.1.3 delta (M-N1…M-N8, M-B1, L-N1…L-N6) is repaired or addressed with a record.
- Both previous harnesses reproduce exactly as claimed: **36 PASS / 1 FAIL / 1 INFO** and **13 PASS / 2 FAIL**, run
  byte-identical (sha256 confirmed against commits `9563192` and `9cb05d8`).
- The complete 4.1.2 → 4.1.3 → 4.1.4 upgrade and 4.1.4 → 4.1.3 → 4.1.2 rollback chain was executed against a consumer
  genuinely created by the 4.1.2 binary: per-transition gates, byte-identical overlay and `spec/` preservation,
  ledgered rollbacks, snapshot consumption, `SNAPSHOT_MISSING` on a third rollback, identical multi-machine manifest
  hash, and correct refusal of re-apply and downgrade.

## Why it is rejected

- **HIGH V-H1 — a plugin descriptor still authorises itself.** `approved_roles: ["all"]` or a fabricated
  `provenance.registered_at` inside the descriptor bypasses `TOOL_POLICY.plugins.min_authority`. An **L0
  `independent-auditor` obtained arbitrary command execution** during `gov rebuild-memory`, and `doctor` D028 reported
  "no plugin problems". This contradicts the candidate's own kernel policy comment and API-0001 §governance, and it
  lands on the four L0 independence roles the protocol depends on (VV-04).
- **HIGH V-H2 — constitutional floors are read from unverified installed-kernel files.** Editing
  `governance/kernel/policies/POLICY_PRECEDENCE.yaml` re-enabled weakening overrides and let an L0 role create tasks;
  editing kernel `SECURITY_POLICY.never_index_classes` removed a restricted-class exclusion at index time. D003,
  `gov kernel verify` and the audit all detect the tampering, but no enforcement path consults them — while the
  *absent-file* path already fails closed to the embedded payload (VV-03c, VV-14).
- **MEDIUM V-M1 — `PROJECT_EXCEPTIONS` decisions are self-attested.** An exception naming a non-existent decision was
  applied. Limited to `exception_relaxable` keys, which include the `MEMORY_POLICY.regression.*` quality floors,
  `CHECKPOINT_POLICY.watchdog.*` and `BUDGET_POLICY.defaults.*` (VV-03a).

NV-09 and NV-19 remain FAIL **only** because they read the immutable, rejected 4.1.3 payload; both underlying defects
are independently confirmed repaired in 4.1.4 (VV-05: 192 kernel YAML files scanned, the sole duplicate key is in the
4.1.3 payload; VV-06: `M-4.1.3-4.1.4` performs and declares the contract tightening). HV-08b remains a non-blocker and
its residual gap M-B1 is now closed by D-0006 and RES-0001.

## Manifest certification block to be recorded by the release owner

This session did not modify `release/releases/4.1.4/manifest.{yaml,json}` or `release/CERTIFICATION_STATUS.md`, in
keeping with the convention established at 4.1.3. Apply the block below verbatim to both manifest files; the kernel
payload and `file_hashes` must stay untouched, and `gov release verify release/releases/4.1.4` remains ok because only
`kernel/` is hashed:

```yaml
certification:
  status: REJECTED
  implementer_evidence: docs/EVIDENCE.md
  independent_verifier: 'Independent Governance OS Verifier and Test Author (fresh re-verification session, Claude Opus 5), 2026-09-12; verdict OS_RELEASE_CANDIDATE_REJECTED; report: release/verification/4.1.4/INDEPENDENT_REVERIFICATION_REPORT.md'
  certified_at: ''
```

Suggested `release/CERTIFICATION_STATUS.md` header:
`Status of 4.1.4: REJECTED (OS_RELEASE_CANDIDATE_REJECTED) — independent re-verification 2026-09-12; report release/verification/4.1.4/INDEPENDENT_REVERIFICATION_REPORT.md`

## Reproduction

```bash
git clone <repo> clone414 && cd clone414 && git checkout v4.1.4-rc1
cargo build --release && cargo test --release --workspace
cargo clippy --workspace --all-targets && cargo fmt --all -- --check
python3 -m pytest capabilities/tests -q

# first verifier's harness, unchanged
GOV_CANONICAL_ROOT=$PWD python3 release/verification/4.1.2/heldout/harness.py

# second verifier's harness, unchanged (needs a 4.1.2 binary)
git worktree add --detach /tmp/wt412 8ad06be && (cd /tmp/wt412 && cargo build --release)
GOV_CANONICAL_ROOT=$PWD GOV412_WORKTREE=/tmp/wt412 \
  python3 release/verification/4.1.3/heldout-new/harness_v2.py

# this session's harness
GOV_CANONICAL_ROOT=$PWD python3 release/verification/4.1.4/heldout-v3/harness_v3.py
```
