# HO-0023 — Handoff for fresh Signed Release Root R0 architecture review

| Field | Value |
|---|---|
| Handoff | HO-0023 |
| From | product-owner-directed governance rebase |
| To | fresh independent R0 architecture reviewer |
| Candidate | D-0009 + ARCH-0003 + `release/root-of-trust/signed-release-root-v1/` |
| Exact Git identity | the committed governance-rebase candidate containing this handoff; reviewer must record `git rev-parse HEAD` before review |
| Active gate | `GATE-R0-ARCH-ACCEPT` |
| Required verdict | `ROT_ARCHITECTURE_ACCEPTED_R0` or `ROT_ARCHITECTURE_REJECTED_R0` |

## Scope

Review only the R0 architecture and declared private/local support envelope. Do not implement. Do not create RoT-1 Revision 8, resume CP-1, activate D-0008/ARCH-0002, supersede D-0007 or alter historical evidence.

## Authoritative inputs

1. `release/orchestration/phase-1/GATES/OWNER-DIRECTIVE-0004-SIGNED-RELEASE-ROOT-REBASE.md`
2. `spec/decisions/D-0009.yaml`
3. `spec/architecture/ARCH-0003.yaml`
4. `release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md`
5. `release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`
6. `release/root-of-trust/signed-release-root-v1/02-OP-1-OP-16-DISPOSITION.md`
7. `release/root-of-trust/signed-release-root-v1/03-TRANSITION-MAP.md`
8. Original Governance OS documents and Capability Acceptance Contract v3, interpreted through D-0009.
9. D-0007 for controls that remain active.
10. Meta-review and historical RoT evidence only where relevant to attacks; neither creates new R0 requirements.

## Required method

For every finding state:

1. exact normative source;
2. original-baseline yes/no and current-owner-approved yes/no;
3. provenance class from the frozen contract;
4. lifecycle/gate;
5. claim falsified or stronger-assurance proposal;
6. security/availability/usability/cost impact;
7. evidence or bounded counterexample;
8. whether owner action is required.

A finding blocks R0 only when its source and lifecycle match R0. R1 implementation mechanics, R2 production evidence and R3 high-assurance controls may be recorded as later conditions but cannot block R0 merely because they are incomplete.

## Mandatory R0 attacks

- Can candidate/project/repository-controlled material establish its own release authority?
- Does every privileged ingress consume the same authenticated-release policy?
- Does metadata bind exact payload, release, platform and migration identities?
- Are root/delegation, rotation, revocation and rollback semantics coherent without universal Trust State?
- Is verify/use byte identity an architecture invariant, including interruption/recovery?
- Is local high-water monotonic and separate from repository state?
- Are stale/offline claims honest and compatible with continued ordinary operation of an authenticated install?
- Can CI or caller-controlled inputs manufacture trust or Human Gate approval?
- Are release authenticity, build provenance, certification, project policy and plugin/retrieval trust actually separated?
- Does the design preserve D-0007 and the original Governance OS/Contract v3 capability architecture?
- Are support assumptions and non-guarantees explicit enough to make the claim testable?

## Acceptance rule

Use the exact R0 rule in the frozen boundary. Acceptance is an architecture verdict only. It opens later owner-authorised R1 planning; it does not authorise implementation by itself.

If rejected, provide an architectural correction delta limited to confirmed R0 defects. Do not route R1/R2/R3 hardening into the correction delta and do not author the replacement during the review.
