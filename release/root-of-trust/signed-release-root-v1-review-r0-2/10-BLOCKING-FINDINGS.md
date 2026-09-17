# 10 — R0 blocking findings (AR-0025, corrected Signed Release Root v1)

## EXPLICITLY EMPTY — no finding blocks `GATE-R0-ARCH-ACCEPT`

This file is deliberately present and deliberately empty of findings, per `HO-0025`
("`10-BLOCKING-FINDINGS.md` (empty or absent if none)"). Its emptiness is a verdict,
not an omission.

**Zero** findings meet the frozen boundary's blocking bar:

> a finding blocks R0 only if its normative source **and** its lifecycle are R0, or if it
> proves an R0 claim internally inconsistent.

## The two prior blockers

| Finding | AR-0023 severity | AR-0025 status | Evidence |
|---|---|---|---|
| `SRR-R0-H1` — floors scoped only to `rollback`; `recovery` admits a floor-free, non-metadata-authenticated restore | HIGH | **CLOSED** | `evidence/PROBES.md` NR-4, NA-1…NA-9 |
| `SRR-R0-M1` — no time/clock assumption or non-guarantee declared | MEDIUM | **CLOSED** | `evidence/PROBES.md` NR-3, NA-10, NA-11 |

Neither is a residual. Each was re-executed against the corrected text rather than
accepted on the correction record's word, and each of AR-0023's five cited floor
statements and its zero-match time sweep was independently re-run and reversed.

## What was found instead, and why none of it blocks

Three conditions and one carried-forward INFO item are recorded in
`20-LATER-LIFECYCLE-CONDITIONS.md`. All are R1 or INFO. None is an R0 blocker, and this
review declines to promote any of them:

- `SRR2-R1-C1` (break-glass exit names only one of the two floors) — a genuine internal
  ambiguity, but the compliant reading is already in the text, no architecture change is
  required to satisfy any R0 guarantee, the state is unreachable without owner-controlled
  break-glass authority, and the clause transcribes `OWNER-DECISION-0006` requirement 7
  faithfully. Flagged `NEW_OWNER_DECISION_REQUIRED` for the orchestrator to route; **not**
  a blocker. Full reasoning at `evidence/PROBES.md` NA-12.
- `SRR2-R1-C2` (offline authenticity record binds release identity; digest granularity
  unstated) — the basis is **not** circular, which was the R0 question; granularity is an
  R1 mechanism with a safe reading available. `evidence/PROBES.md` NA-8.
- `SRR2-R1-C3` (high-water durability across uninstall not stated as explicitly as the
  break-glass case) — the safe reading is stated; R1 already tests high-water durability
  and monotonicity. `evidence/PROBES.md` NA-13.
- `SRR-R0-L8` (traceability table maps 11 of 14 R0 items) — carried forward from AR-0023 at
  unchanged INFO severity. AR-0024 disclosed that it did not fix this; that disclosure is
  accurate and both of its re-pointed rows verify. `evidence/PROBES.md` NA-16.

## Findings deliberately NOT raised, for the record

- `SRR-R0-L6` — owner-deferred to R1 by `OWNER-DECISION-0005` §2 and expressly barred from
  being raised as an R0 blocker by any later R0 reviewer of this lineage. Not raised.
- `SRR-R0-L7` — owner-closed as out of scope for the private/local profile by
  `OWNER-DECISION-0005` §3. Not raised.
- `SRR-R0-L1`…`L5`, `L9` — carried at their AR-0023 lifecycles, unchanged by the
  correction and not reopened.
- Production ceremonies, DDC/diverse compilers, supplier independence, reproduction quorum,
  multi-source first contact, public/cloud/hostile-admin assurance, Gate W/G6 completion and
  platform certification — excluded from R0 by the frozen boundary and not assessed as defects.
- The trust chain, metadata model, metadata role table, domain-separation table, ingress set,
  transaction invariant, bootstrap assumption, CI/headless model, D-0007 transition rule and
  non-goals — uncontested at AR-0023. This review found **no cause** to reopen any of them,
  and reopened none.
