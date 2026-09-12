# Independent re-verification verdict — repair candidate 4.1.3

Candidate commit verified: `26ab5b6eb111d573f8686bc4f4b1dfc20539f45e` (branch `release/4.1.2-rc1`, payload `release/releases/4.1.3`, release_hash `6bebfdbb503c9dc142b7951c8635775d8af61ada0f7a1e96005531451b3627d1`).

**Verdict: OS_RELEASE_CANDIDATE_REJECTED** (repairable — see `INDEPENDENT_REVERIFICATION_REPORT.md` §11–§12).

Headline defects found by the new held-out harness (`heldout-new/harness_v2.py`, 6 PASS / 9 FAIL):
- CRITICAL C-N1 — `cit approve --method human` succeeds with a presented-but-unanswered gate and after the human answered B; the declined CIT executes (NV-01).
- HIGH H-N1 — `PROJECT_POLICY.policy_overrides` silently lowers AUTHORITY_POLICY levels and empties SECURITY_POLICY.never_index_classes (NV-02).
- HIGH H-N2 — plugin descriptors execute arbitrary commands for any role, unregistered, unpinned, unvalidated (NV-04).
- MEDIUM — lock `release_commit` provenance, absolute `source` after update, incomplete `M-4.1.2-4.1.3`, self-attested mutation scope, record loss on incremental rebuild after relocation, API-0001 contradicting the fail-closed implementation.

Previous CRITICAL/HIGH findings (C1, C2, H1–H7): genuinely repaired; first verifier's harness unchanged: 36 PASS / 1 FAIL (HV-08b) / 1 INFO. HV-08b is not a release blocker (report §5).

## Manifest certification block to be recorded by the release owner

This session was not permitted to modify `release/releases/4.1.3/manifest.{yaml,json}` or `release/CERTIFICATION_STATUS.md`. Per `docs/RELEASE.md` only an independent verifier may set REJECTED; the block below is the verifier's record. Apply it verbatim to both manifest files (the kernel payload and `file_hashes` must stay untouched; `gov release verify release/releases/4.1.3` remains ok because only `kernel/` is hashed):

```yaml
certification:
  status: REJECTED
  implementer_evidence: docs/EVIDENCE.md
  independent_verifier: 'Independent Governance OS Verifier (fresh re-verification session, Claude Fable 5.1), 2026-09-12; verdict OS_RELEASE_CANDIDATE_REJECTED; report: release/verification/4.1.3/INDEPENDENT_REVERIFICATION_REPORT.md'
  certified_at: ''
```

Suggested `release/CERTIFICATION_STATUS.md` header: `Status of 4.1.3: REJECTED (OS_RELEASE_CANDIDATE_REJECTED) — independent re-verification 2026-09-12; report release/verification/4.1.3/INDEPENDENT_REVERIFICATION_REPORT.md`.

## Reproduction

```bash
cargo clean && cargo build --release
python3 release/verification/4.1.2/heldout/harness.py                        # first verifier's harness, unchanged
git worktree add --detach /tmp/wt-412 8ad06be && (cd /tmp/wt-412 && cargo build --release)
GOV412_WORKTREE=/tmp/wt-412 python3 release/verification/4.1.3/heldout-new/harness_v2.py
```
