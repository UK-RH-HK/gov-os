# P2-HO-0046 — Verification iteration 1: AC-6 Qualification Oracle format review

| Field | Value |
|---|---|
| Handoff | P2-HO-0046 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent **oracle-format reviewer**, run **P2-AR-0045** |
| Candidate | `cap2-candidate-1` (identities in your dispatch message and `ORCHESTRATOR_STATE.yaml`) |
| Gate | `GATE-P2-ORACLE-FORMAT` (frozen contract AC-6, §9.2) |
| Evidence directory | `release/capability-baseline/verify-1/oracle-format/` |
| Required verdict | `ORACLE_FORMAT_ACCEPTED` or `ORACLE_FORMAT_REJECTED` (with the failing requirements), or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0043-verify-1-common-protocol.md`; the frozen gate contract AC-6 and §9.2; Contract v3
Gate V (lines 1012–1065: V1 fault manifest, V2 hidden path-map oracle, V3 hidden memory oracle, V4 quantitative
qualification scoring) and every other Contract v3 line that constrains hidden-oracle material (e.g. its separation from
public suites and governed repositories); iteration-0 class BC-P2-51 in
`release/capability-baseline/audit-0/synthesis/{blocker-classes.yaml,repair-delta.md}`.

## What you decide

Whether a Qualification Oracle **format** covering V1–V4 exists on this candidate as a **machine-checkable definition**, and
whether you accept it. The format is a Phase-2 artefact; **no hidden fault is generated in Phase 2**, and you generate none.
Format samples you write to test the definition are labelled samples, kept in your evidence directory, never presented as
an oracle.

1. **Identify the format.** The candidate's schema (`framework/qualification-oracle/`), its validator
   (`runtime/src/qualification_oracle.rs`, `gov oracle …`), and the digest the product reports for the format
   (`format_sha256`). Record the digest you observe; round-1 WS-1/12 reported `f89a3e2f…16fd` — if it differs, find why
   and whether the change is to the format itself.
2. **Coverage.** Every V1–V4 bullet maps to required, typed fields and validation rules. A bullet the format cannot express,
   or expresses only as free text where the contract requires something checkable (e.g. expected detection, severity,
   scoring arithmetic), is a finding.
3. **Machine-checkability, by attack.** Write valid and invalid sample documents per bullet (missing field, wrong type,
   unbound score report, arithmetic mismatch, unscored injected fault, oracle not separate from the public suite or from a
   governed repository, oracle material inside a governed repository) and show the validator accepts exactly the valid ones
   with typed errors for the rest. Include the G6 entry point: a qualification run is recorded only against a conforming,
   separate, bound oracle; a `FORMAT_SAMPLE` never counts as qualification.
4. **Fitness for Phase 4.** Could a later qualification author write a real hidden oracle and score report in this format
   without inventing fields the contract requires? Record gaps; do not design a replacement.

Output under your evidence directory: `00-ORACLE-FORMAT-REVIEW.md` (verdict first; V1–V4 bullet-by-bullet coverage;
attacks and results; the accepted `format_sha256`), `findings.yaml` (common-protocol schema), `samples/`, `evidence/`. Your
run report records the verdict and, when accepting, the exact `format_sha256` you accepted.
