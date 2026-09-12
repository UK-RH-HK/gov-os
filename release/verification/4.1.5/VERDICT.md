# Independent re-verification verdict — repair candidate 4.1.5

Candidate verified: commit `da9c8518d3fddba6f37bafb4d046ca313335ec1f` (branch `release/4.1.5-rc1`, tag `v4.1.5-rc1`,
payload `release/releases/4.1.5`, release_hash `962f98480fc311c5857e7eef6f951f5713c3e62e4b1e9703c8c5d1f5c74a314b`).

**Verdict: OS_RELEASE_CANDIDATE_REJECTED** (repairable — see `INDEPENDENT_REVERIFICATION_REPORT.md` §11–§13).

## What the repair achieved

- **V-H1 repaired** — the plugin authority floor comes from verified kernel policy and applies to every execution;
  `approved_roles`/`provenance`/`status` in a descriptor are advisory; registration is an OS-written registry binding
  id+version+descriptor-sha256+impl-sha256. A self-declaring descriptor, a forged `provenance`, a **hand-forged registry
  entry**, an edited descriptor and an L0 rebuild of a registered plugin were all refused/inert (WV-01; VV-04 now PASS).
- **V-H2 repaired** — a present-but-tampered installed kernel makes `kernel trust verified:false`, substitutes the
  embedded baseline explicitly, and refuses every mutating operation `KERNEL_TAMPERED`; overrides are L4+ and bound to a
  fingerprint of the exact kernel state; read paths survive and surface the substitution (WV-02; VV-03/VV-14 now PASS).
- **V-M1 repaired** — an exception applies only for a real, current, in-scope, sufficiently-approved decision, and never
  for a security/authority key even with a valid decision (WV-03; VV-03 now PASS).
- **ETXTBSY repaired** — 24 concurrent write-then-exec plugin invocations, 0 spawn failures (WV-05).
- **D-0007 tool-install self-attestation repaired** — `security_review:passed` counts only with a governed
  `security_review_record` (WV-04).
- Every 4.1.2/4.1.3/4.1.4 CRITICAL/HIGH repair is preserved; six architecture pillars upgraded PARTIAL→P&S; nothing
  regressed. All three previous harnesses reproduce (36/1/1, 13/2, 14/2), the residual failures being confirmed
  frozen-input/identity artefacts. The 4.1.5 payload is byte-identical to `framework/` at its release commit, reproduces
  the same `release_hash`, is immutable, carries no duplicate keys, and `M-4.1.4-4.1.5` truthfully declares its changes.
  The full 4.1.2→…→4.1.5 upgrade/rollback chain works with per-hop gates, byte-identical overlay/`spec` preservation,
  ledgered rollbacks and identical multi-machine hashes.

## Why it is rejected

- **HIGH V-H3 — `gov update` and `gov init` do not authenticate the update/install SOURCE payload.** They stage the
  source and regenerate `KERNEL_MANIFEST.json` and `framework.lock.kernel_manifest_hash` from the installed bytes, so the
  V-H2 trust root attests only internal self-consistency, not authenticity. A tampered 4.1.5 source with
  `SECURITY_POLICY.never_index_classes` stripped of `restricted` (its shipped `manifest.json`/`KERNEL_MANIFEST.json` left
  stale) installed through a properly answered gate; afterward `gov kernel trust` reported **`verified: true`**, doctor
  was clean, and a **restricted material record became indexed and retrievable** (excluded `sensitivity:restricted` on an
  intact-kernel control). `gov release verify` detects the tampered source and the resulting `lock.release_hash`
  (`47d080e4…`) diverges from the published `962f9848…`, but nothing in the update/init flow performs or prompts either
  check. `gov init` from the tampered `kernel/` also reports `verified:true`. Evidence:
  `release/verification/4.1.5/evidence/V-H3-update-source-not-authenticated.md` and the migration-chain report Step 8.

This is the install/update-time instance of exactly the "a lower-trust input may never manufacture a higher-trust fact"
pattern D-0007 was written to close — the fourth consecutive iteration of a trust-anchor-authenticity defect. The report
§13 records a root-cause escalation recommendation for the owner alongside the bounded repair delta (§12).

## Manifest certification block to be recorded by the release owner

This session did not modify `release/releases/4.1.5/manifest.{yaml,json}` or `release/CERTIFICATION_STATUS.md`. Apply the
block below verbatim to both manifest files; the kernel payload and `file_hashes` must stay untouched, and
`gov release verify release/releases/4.1.5` remains ok because only `kernel/` is hashed:

```yaml
certification:
  status: REJECTED
  implementer_evidence: docs/EVIDENCE.md
  independent_verifier: 'Independent Governance OS Verifier and Test Author (fresh re-verification session, Claude Opus 4.8/5), 2026-09-12; verdict OS_RELEASE_CANDIDATE_REJECTED; report: release/verification/4.1.5/INDEPENDENT_REVERIFICATION_REPORT.md'
  certified_at: ''
```

Suggested `release/CERTIFICATION_STATUS.md` header:
`Status of 4.1.5: REJECTED (OS_RELEASE_CANDIDATE_REJECTED) — independent re-verification 2026-09-12; report release/verification/4.1.5/INDEPENDENT_REVERIFICATION_REPORT.md`

## Reproduction

```bash
git clone <repo> clone415 && cd clone415 && git checkout v4.1.5-rc1
cargo build --release && cargo test --release --workspace
cargo clippy --workspace --all-targets && cargo fmt --all -- --check
python3 -m pytest capabilities/tests -q

# three previous verifier harnesses, unchanged
GOV_CANONICAL_ROOT=$PWD python3 release/verification/4.1.2/heldout/harness.py
git worktree add --detach /tmp/wt412 8ad06be && (cd /tmp/wt412 && cargo build --release)
GOV_CANONICAL_ROOT=$PWD GOV412_WORKTREE=/tmp/wt412 python3 release/verification/4.1.3/heldout-new/harness_v2.py
GOV_CANONICAL_ROOT=$PWD python3 release/verification/4.1.4/heldout-v3/harness_v3.py

# this session's fourth held-out harness
GOV_CANONICAL_ROOT=$PWD python3 release/verification/4.1.5/heldout-wv/harness_wv.py

# V-H3 reproduction: build a 4.1.2 or 4.1.4 consumer, copy release/releases/4.1.5 to a scratch dir,
# remove `restricted` from kernel/policies/SECURITY_POLICY.yaml never_index_classes (leave manifests stale),
# gov update --apply --approve through the gate, then: gov kernel trust  ->  verified:true (defect).
```
