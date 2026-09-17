# 10 — R0 blocking findings (AR-0023, Signed Release Root v1)

Two findings block `GATE-R0-ARCH-ACCEPT`. Each states all eight fields required by
the frozen boundary §"Finding intake contract" and the role instruction.

A finding appears here only because **its normative source and its lifecycle both
match R0**, or because it proves an R0 claim internally inconsistent. No R1
implementation mechanic, R2 production evidence or R3 high-assurance control is
present in this file.

---

## SRR-R0-H1 — HIGH — Signed rollback floors are scoped only to `rollback`; the `recovery` ingress admits a floor-free, non-metadata-authenticated restore

### 1. Exact normative source

- `01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` §"R0 — Root/Release Architecture Acceptance", **item 5** ("one verification policy across init, adopt, update, reinstall, rollback and recovery") and **item 8** ("signed rollback floors and protected local high-water").
- `OWNER-DIRECTIVE-0004` §"Freshness, CI and authority": "Clients retain the highest valid metadata/minimum secure release observed and **refuse rollback below local high-water**."
- `OWNER-DIRECTIVE-0004` §"Decision and evidence disposition": D-0007's "manifest and `framework.lock` remain post-install integrity and release-pin records; **they are not the first-install authenticity root**."
- `Governance_OS_Capability_Acceptance_Contract_v3.md` §A2 **[POST-VERIFICATION HARDENING]**: "Init/adopt/update/reinstall/**recovery**/rollback ingress paths share a non-circular trust root", and the A2 advanced qualification challenge, which names "downgrade/replay attempt".
- Internally inconsistent with the candidate's own text: `ARCH-0003.yaml:47` and `00-ARCHITECTURE.md:32`.

### 2. Provenance class

`NECESSARY-DERIVED`. The floor rule and the six-ingress uniformity rule are both
owner-approved and already present; applying the floor to the `recovery` ingress is
not a new requirement but the necessary consequence of the two existing ones. I am
not proposing a new control.

### 3. Baseline and approval status

- Original-baseline: **yes** — Contract v3 A2 already enumerates `recovery` among the ingress paths that must share the non-circular trust root, and already names downgrade/replay as an A2 challenge.
- Current-owner-approved: **yes** — frozen boundary R0 items 5 and 8, and OWNER-DIRECTIVE-0004's explicit "refuse rollback below local high-water".

### 4. Lifecycle / gate

**R0.** The defect is in the architecture's specification of which authority admits
which ingress. It is not an implementation mechanic: an R1 implementer cannot
resolve it, because the architecture supports two contradictory implementations
with opposite fail-closed behaviour and does not say which is correct.

### 5. Explicit claim falsified

Two, both stated by the candidate:

1. `00-ARCHITECTURE.md:32` (§"Security objective"): "**rollback below known signed floors is refused**."
2. `ARCH-0003.yaml:47` (§3, chain step 6): "**One verifier evaluates the same policy** for init, adopt, update, reinstall, rollback and recovery."

This is not a stronger-assurance proposal. It falsifies claims the candidate makes
about itself.

### 6. Evidence

Probe PR-5 (`evidence/PROBES.md`) enumerated every floor term and every recovery
term in the two architecture documents. Result:

Every floor-bearing statement is lexically scoped to **`rollback`**:

- `ARCH-0003.yaml:86-87` — "Clients persist the highest valid root/metadata versions and minimum secure release they have observed. **Rollback** below those floors is refused."
- `00-ARCHITECTURE.md:32` — "**rollback** below known signed floors is refused"
- `00-ARCHITECTURE.md:104` — "A signed minimum secure release prevents unsafe **rollback**…"
- `00-ARCHITECTURE.md:79`, ingress table, **rollback** row — required authenticated object: "signed release not below security/high-water floor"
- `00-ARCHITECTURE.md:103` — "A client never accepts an older **metadata** version than its protected high-water" — binds *metadata* versions, which the path below never consults.

The `recovery` row of the same table (`00-ARCHITECTURE.md:80`) reads in full:

| Ingress | Required authenticated object | Local authority | State effect |
|---|---|---|---|
| recovery | authenticated recovery target **or installed valid recovery path** | bounded local recovery authority | restore one complete valid state |

It is the only one of the six rows whose required authenticated object admits an
alternative outside the signed-metadata policy, and the only backward-capable row
with no floor term. The adjacent `rollback` row carries the floor explicitly — the
contrast is within a single table.

### 7. Bounded counterexample

All steps are inside the declared private/local support envelope. No hostile
administrator, no compromised OS, no network attacker and no multi-tenant
assumption is used.

1. Machine `M` runs an authenticated Governance OS `v5`. Its protected local state holds high-water `v5` and signed minimum secure release `v5`; `v4` was withdrawn for a security defect and a validly signed metadata set revoking it has been received and retained ("protected state prevents forgetting it").
2. A complete, self-consistent `v4` installation remains present in `M`'s local recovery/journal area — the normal residue of the `v4`→`v5` update, whose transaction invariant preserves "the old complete version" precisely so that recovery is possible.
3. An operator with "bounded local recovery authority" invokes the `recovery` ingress after an unrelated fault.
4. The `recovery` ingress selects its second admissible object, the "installed valid recovery path" `v4`. Its validity is established by D-0007 installed-integrity records — payload ↔ `KERNEL_MANIFEST.json` ↔ `framework.lock` — which are mutually self-consistent for `v4` and which OWNER-DIRECTIVE-0004 states are *not* an authenticity root.
5. Nothing in the specified `recovery` ingress consults the signed minimum secure release or the local high-water: the floor rule names `rollback`, and `00-ARCHITECTURE.md:103` binds only metadata versions, while this path consults no metadata at all.
6. `M` is restored to revoked `v4`. Per `ARCH-0003.yaml:91`, a "known revoked binary is limited to inspection, export, **recovery** and uninstall" — so the revoked binary may itself re-invoke the same ingress, and whether it even recognises its own revocation depends on protected local state the architecture does not require this path to read.

Outcome: a downgrade to a revoked release, laundered through `recovery`, on a
machine whose stated guarantee is that rollback below known signed floors is
refused. The counterexample requires no attacker at all — an ordinary operator
recovery reaches it.

### 8. Security / availability / usability / cost consequence

- **Security:** defeats the downgrade-and-revocation protection that R0 item 8 exists to establish, by the one route that consults no signed metadata. This is the precise class the SRR-1 lineage was created to close.
- **Availability:** the opposite reading is not free either, and this is the real trade-off. If the floor binds `recovery` unconditionally, a machine whose only complete local state is below its own signed floor becomes unrecoverable — the "availability under strict freshness" degradation the forensic meta-review warned about. The architecture must choose, and say which.
- **Usability:** an operator invoking recovery during an incident cannot currently predict whether the system will refuse; both behaviours are consistent with the text.
- **Cost:** low. The correction is a scope statement plus, if the owner wants a break-glass path, a named authority for it.

### 9. Owner action required

**Yes — one bounded trade-off**, recorded as `NEW-OWNER-DECISION-REQUIRED` inside
this finding. The owner must decide whether below-floor recovery is:

- (a) always refused (strongest downgrade protection; accepts that a machine with no at-or-above-floor complete local state must be re-initialised from an authenticated release); or
- (b) permitted only under an explicit, separately authorised local break-glass authority, recorded and reported, with the machine's state marked accordingly.

I do not choose between these and I do not author the mechanism. Either choice
closes the finding provided the architecture states it and scopes the floor rule
explicitly across all six ingresses.

---

## SRR-R0-M1 — MEDIUM — No time/clock assumption or non-guarantee is declared, although the entire expiry/freshness/stale-honesty model is evaluated against it

### 1. Exact normative source

- `01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` §"R0", **item 12**: "local OS/admin/**time**/network assumptions and explicit non-guarantees." Time is enumerated as a distinct required declaration, separately from OS/admin and separately from network.
- Same document, **item 10**: "explicit stale, expired and offline states without false revocation knowledge."
- Same document, §"R0 acceptance", clause 1: "every R0 item above is **explicit**, internally consistent and **testable at later gates**."
- `Governance_OS_Capability_Acceptance_Contract_v3.md` §"Evidence freshness" (a previously green capability becomes `STALE` when relevant evidence inputs change) and §A2 bullet 10 (offline verification behaviour), both of which require a defined freshness basis.

### 2. Provenance class

`OWNER-ADDED-NORMATIVE`. The obligation to declare the time assumption is created
by the owner's own frozen boundary item 12. I am not importing an external
hardening requirement and I am not asking for a trusted-time mechanism.

### 3. Baseline and approval status

- Original-baseline: **partly** — the original documents require honest freshness and staleness semantics but do not enumerate a time declaration.
- Current-owner-approved: **yes** — frozen boundary item 12 enumerates "time" explicitly, and the boundary is `OWNER-FROZEN BY OWNER-DIRECTIVE-0004`.

### 4. Lifecycle / gate

**R0.** Item 12 is an R0 item and the required artefact is a declaration in the
architecture record, not an implementation. The duration *parameters* are correctly
deferred to R1/R2 and I do not ask for them; what is missing is the assumption the
parameters will be evaluated against.

### 5. Explicit claim affected

`00-ARCHITECTURE.md:32` (§"Security objective"): "**stale/unknown currency is
reported honestly**", and `ARCH-0003.yaml:92`: "Offline clients report currency
stale/unknown and never claim knowledge of unseen revocations."

The claim is not shown false — it is shown **not testable**. "Stale", "expired" and
"current" are defined by comparing signed expiry fields to a time source that the
candidate never names, never bounds and never declares trusted or untrusted. An R1
verifier cannot write a passing or failing test for "reports currency honestly"
without knowing whether the clock is assumed correct, how far it may drift before
the claim is void, and what the system must report when the basis is unreliable.

### 6. Evidence

Probe PR-3 (`evidence/PROBES.md`): a case-insensitive sweep of all seven
authoritative inputs for `clock|time|wall|NTP` — excluding the compound words
`timestamp`, `runtime`, `lifetime`, `sometimes` — returns **zero matches**. The
word `timestamp` occurs only as the name of the TUF metadata role. The candidate's
declared-assumption statements are:

- `ARCH-0003.yaml:28-32` — "R0 assumes the local OS, administrator and bootstrap installation boundary are uncompromised… does not claim protection from a hostile administrator/OS, public multi-tenant isolation, absolute compiler correctness or knowledge of revocations that an offline machine has never received."
- `00-ARCHITECTURE.md` §"Declared Phase-1 environment" — six bullets: controlled machines, private repositories, local/administrator-controlled installation, no public multi-tenant boundary, no hostile local administrator/OS claim, no DDC/supplier/toolchain claim.

OS ✓, admin ✓, bootstrap ✓, network ✓ (via the offline/stale semantics and the
unseen-revocations non-guarantee). Time ✗.

The omission is substantive rather than pedantic precisely because the boundary
separates "time" from both "OS/admin" and "network": in this architecture the local
OS is **trusted** and the network is **untrusted**, and a clock is ordinarily
derived from both. A reader cannot determine from the candidate which side of that
line the time source falls on, and the two readings give different answers to the
freeze/replay attack (A-07) and to the honesty claim.

### 7. Bounded counterexample

Machine `M` is inside the declared envelope — uncompromised OS, trusted
administrator — but its clock is materially wrong, through ordinary
misconfiguration, a dead RTC battery, a VM snapshot restore or a timezone/epoch
fault. No attacker is required.

- Clock behind: expired root/targets/snapshot/timestamp metadata evaluates as unexpired. `M` performs trust-changing lifecycle operations that the architecture states must be blocked, and reports currency as current rather than `STALE`/`UNKNOWN` — directly contradicting the honesty claim in §5.
- Clock ahead: valid current metadata evaluates as expired. `M` blocks trust-changing operations it should permit; a support envelope that promises an authenticated install is "not automatically bricked" degrades in a way the architecture does not describe.

Both outcomes are reachable within the declared envelope, and the architecture
provides no statement that either is in or out of scope.

### 8. Security / availability / usability / cost consequence

- **Security:** the stated defence against metadata freeze/replay (short-lived timestamp metadata blocking trust-changing operations) rests on an undeclared premise. Under the trusted-OS reading it holds; under the untrusted-network-time reading it does not. The architecture must say which.
- **Availability:** an undeclared clock assumption leaves the "does not brick an authenticated install" promise without a stated boundary in the clock-ahead case.
- **Usability:** an operator cannot tell whether a `STALE` report means "genuinely stale" or "clock wrong".
- **Cost:** very low. A declared assumption and a conditional honesty claim. I am explicitly **not** requiring a trusted-time service, a monotonic-time mechanism, an attestation, or any R1/R2/R3 control.

### 9. Owner action required

**No.** This is a completion of an assumption list the owner already mandated, not
a new trade-off. The architecture owner can close it in the R0 revision. If the
owner separately wishes to add a time-independent freshness mechanism, that is a
stronger-assurance proposal requiring owner adoption and is **not** required here —
it is recorded nowhere as a condition.

---

## Findings explicitly NOT raised as blockers

For the record, and to keep this review inside its provenance discipline, the
following were tested and deliberately **not** promoted to R0 blockers:

- Contract v3 A2 bullet 8 (dev/test trust modes vs certified production) — no such mode exists in the candidate or in the shipped source (probe PR-4), so no claim is falsified. R1 condition `SRR-R0-L4`.
- Root succession/rotation chaining — imported by reference from "a mature TUF-style metadata model"; the frozen boundary enumerates rotation *semantics*, which are stated, and defers library selection. R1 condition `SRR-R0-L1`.
- Release channel binding — not an enumerated R0 binding. R1 condition `SRR-R0-L2`.
- Plugin/tool/skill acquisition not consuming the release verifier — the frozen boundary's R0 item 11 deliberately scopes plugin/retrieval trust into a *separate* domain, and Contract v3 F2/F3/F4 govern it without requiring source signing. Recorded as `SRR-R0-L6`, `NEW-OWNER-DECISION-REQUIRED`, non-blocking.
- Private staging occurring before verification — this is the standard and unavoidable download-then-measure order; the staging area is private and no privileged material is installed unverified. No defect.
- All R2/R3 matters (production signatures, custody, two independent verification records, SBOM, reproducibility quorum, DDC, supplier independence, multi-source first contact, G6/Gate W completion) — excluded by the frozen boundary and not assessed as defects.
