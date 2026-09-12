# Certification status — agentic-engineering-os 4.1.2

**Status: REJECTED (OS_RELEASE_CANDIDATE_REJECTED) — independent verification 2026-09-12**

Independent verifier: fresh session, no builder context. Full report, matrices, gap register and repair delta:
[release/verification/4.1.2/INDEPENDENT_VERIFICATION_REPORT.md](verification/4.1.2/INDEPENDENT_VERIFICATION_REPORT.md).
Held-out harness and results: `release/verification/4.1.2/heldout/`.

Summary: the builder's suites reproduce on a clean build (15/15 certification, 10/10 unit, 4/4 plugin) and the core is a
substantial Rust implementation, but 37 held-out scenarios expose 2 CRITICAL and 7 HIGH defects: the retrieval query is
always embedded with the built-in embedder regardless of the pinned plugin; the plugin host deadlocks on responses larger
than the pipe buffer; authority levels, mutation scope at task close, restricted sensitivity classes and destructive
migration gates are not enforced; claims are dropped by a full rebuild; an embedder pin change leaves a mixed index that
freshness/doctor report as healthy; no reranker hook and no benchmark/selection mechanism exist.

Previous implementer status (READY_FOR_INDEPENDENT_OS_VERIFICATION) is superseded by this verdict. The release manifest
`certification.status` is REJECTED. After the repair delta is applied, a new independent verification is required.

---

## Implementer statement (2026-09-12, before verification)

The implementer (this repository's orchestrator session) has:
1. implemented the framework as software (kernel payload, Rust core, `gov` CLI, plugin protocol, migrations);
2. built seven synthetic certification fixtures and an implementer certification harness (`tests/certification/`);
3. recorded implementer evidence in `docs/EVIDENCE.md` and `release/evidence/`.

The implementer has **not** certified the release (protocol §6: "A framework developer must not be the only final
verifier of a release candidate"). Independent verification must:
- run `cargo test` from a fresh clone;
- re-execute the seven fixture scenarios and the negative controls independently of the harness assertions;
- audit the kernel payload against the governing documents;
- record the verdict (`CERTIFIED` or `REJECTED`) in `release/releases/4.1.2/manifest.yaml` → `certification`.

---

## Implementer repair statement (2026-09-12, after the rejection)

Repair iteration applied on branch `release/4.1.2-rc1` (not merged to `main`), producing repair candidate **4.1.3**
(`release/releases/4.1.3/`, kernel payload changed → new immutable version; 4.1.2 stays REJECTED and untouched).

- Repair mapping (every CRITICAL/HIGH → root cause / change / builder regression test / held-out result):
  [release/repair/4.1.3/REPAIR_REPORT.md](repair/4.1.3/REPAIR_REPORT.md).
- Unchanged independent harness rerun: `release/verification/4.1.2/heldout-rerun/` — 36 PASS / 1 FAIL (HV-08b,
  MEDIUM, baseline-embedder paraphrase; documented residual) / 1 INFO / 0 ERROR (verifier run: 12 / 25 / 1 / 0).
- Builder evidence: `docs/EVIDENCE.md` (35/35 certification, 14/14 unit, 4/4 plugin; clippy and rustfmt ran).
- Verifier artefacts were not modified; no verifier-authored test was changed.

**Status of 4.1.3: READY_FOR_INDEPENDENT_REVERIFICATION — certification pending.** The implementer has not issued
`OS_RELEASE_CANDIDATE_ACCEPTED` and must not; the 4.1.3 manifest `certification.status` records the pending state.
Repair code commit: `78f6853`; the repair candidate commit adds `release/releases/4.1.3/` on top of it (hash in the handoff message and `git log`).


---

## Status of 4.1.3: REJECTED (OS_RELEASE_CANDIDATE_REJECTED) — independent re-verification 2026-09-12; report release/verification/4.1.3/INDEPENDENT_REVERIFICATION_REPORT.md

Recorded by the release owner verbatim from the verifier's `release/verification/4.1.3/VERDICT.md` (the verifier was
not permitted to edit shared release files). The 4.1.3 manifest certification block carries the same text; the kernel
payload and `file_hashes` are untouched (`gov release verify release/releases/4.1.3` remains ok). Verifier artefacts
under `release/verification/4.1.3/` were not modified.

## Implementer repair statement (2026-09-12, second repair iteration)

Repair candidate **4.1.4** on branch `release/4.1.4-rc1` (tag `v4.1.4-rc1` at the candidate commit; the rejected
4.1.3 candidate is tagged `v4.1.3-rc1` at `26ab5b6`). Repair mapping for every finding of the re-verification:
[release/repair/4.1.4/REPAIR_REPORT.md](repair/4.1.4/REPAIR_REPORT.md). Both independent harnesses were rerun
unchanged (`release/verification/4.1.2/heldout-rerun-4.1.4/`, `release/verification/4.1.3/heldout-new-rerun-4.1.4/`).

**Status of 4.1.4: READY_FOR_INDEPENDENT_REVERIFICATION — certification pending.** The implementer has not issued
`OS_RELEASE_CANDIDATE_ACCEPTED` and must not.

---

## Status of 4.1.4: REJECTED (OS_RELEASE_CANDIDATE_REJECTED) — independent re-verification 2026-09-12; report release/verification/4.1.4/INDEPENDENT_REVERIFICATION_REPORT.md

Recorded by the release owner verbatim from the verifier's `release/verification/4.1.4/VERDICT.md` (that session did
not edit shared release files). The 4.1.4 manifest certification block carries the same text; the kernel payload and
`file_hashes` are untouched, so `gov release verify release/releases/4.1.4` remains ok. Verifier artefacts under
`release/verification/4.1.4/` were not modified.

The 4.1.4 verification confirmed C-N1, H-N1 and every MEDIUM/LOW item of the 4.1.3 delta as repaired, and rejected the
candidate on two HIGH trust-root defects (V-H1 plugin descriptors authorising themselves; V-H2 constitutional floors
read from an unverified installed kernel) and one MEDIUM (V-M1 self-attested policy exceptions).

## Implementer repair statement (2026-09-12, third repair iteration)

Repair candidate **4.1.5** on branch `release/4.1.5-rc1` (tag `v4.1.5-rc1` at the candidate commit; rejected candidates
keep their tags `v4.1.3-rc1` and `v4.1.4-rc1`). Repair mapping for every finding:
[release/repair/4.1.5/REPAIR_REPORT.md](repair/4.1.5/REPAIR_REPORT.md). All three independent harnesses were rerun
unchanged (`release/verification/4.1.2/heldout-rerun-4.1.5/`, `release/verification/4.1.3/heldout-new-rerun-4.1.5/`,
`release/verification/4.1.4/heldout-v3-rerun-4.1.5/`).

**Status of 4.1.5: READY_FOR_INDEPENDENT_REVERIFICATION — certification pending.** The implementer has not issued
`OS_RELEASE_CANDIDATE_ACCEPTED` and must not.
