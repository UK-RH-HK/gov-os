# 04 — R0 correction 1 (SRR-1): the bounded repair of `SRR-R0-H1` and `SRR-R0-M1`

| Field | Value |
|---|---|
| Record | `R0-CORRECTION-1` |
| Run | AR-0024, role `r0-architecture-correction` |
| Handoff | `release/orchestration/phase-1/HANDOFFS/HO-0024-srr1-r0-bounded-correction.md` |
| Base commit | `73227a1594265743b18eb7115394d639e6c659a2` |
| Candidate corrected | D-0009 + ARCH-0003 + `release/root-of-trust/signed-release-root-v1/` |
| Rejection corrected | AR-0023, `ROT_ARCHITECTURE_REJECTED_R0`, reviewed candidate `5fd8358`, work commit `2dc08c2` |
| Specification followed | `release/root-of-trust/signed-release-root-v1-review-r0/11-CORRECTION-DELTA.md` (CD-R0-1, CD-R0-2) |
| Owner inputs | `OWNER-DECISION-0006` (sha256 `903407729327d67c198c9bf97885a936c5601993e16ad76137a3106c5728d1db`); `OWNER-DECISION-0005` |
| Frozen contract | `01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`, sha256 `70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1`, unchanged by this correction |
| Cycle | bounded R0 correction cycle 1 of 1 |
| Status asserted | **none**. This record does not claim R0 acceptance and does not grade itself. A fresh independent R0 reviewer grades the corrected candidate. |

## Scope actually applied

Two text-level corrections in two documents, plus this record. No component, boundary, trust direction or lifecycle
gate was changed. The trust chain, metadata model, metadata role table, domain-separation table, lifecycle ingress
set, transaction invariant, bootstrap assumption, CI/headless model, D-0007 transition rule and non-goals are
untouched: the rejection did not contest them.

Files changed by `R0-CORRECTION-1`:

1. `spec/architecture/ARCH-0003.yaml`
2. `release/root-of-trust/signed-release-root-v1/00-ARCHITECTURE.md`
3. `release/root-of-trust/signed-release-root-v1/04-R0-CORRECTION-1.md` (this file, new)

Line references below are to `73227a1` for prior text and to the corrected files for corrected text.

---

## CD-R0-1 — closes `SRR-R0-H1` (HIGH)

**Finding.** Signed rollback floors were scoped only to the `rollback` ingress, and the `recovery` ingress admitted a
floor-free, non-metadata-authenticated restore. Frozen R0 items **5** (one verification policy across
init/adopt/update/reinstall/rollback/recovery) and **8** (signed rollback floors and protected local high-water) were
recorded as not satisfied on that evidence.

**Normative sources.** Frozen boundary R0 items 5 and 8; `OWNER-DIRECTIVE-0004` §"Freshness, CI and authority"
("refuse rollback below local high-water") and §"Decision and evidence disposition" (manifest/lock "are not the
first-install authenticity root"); Contract v3 §A2 (`Init/adopt/update/reinstall/recovery/rollback ingress paths share
a non-circular trust root`, and the A2 downgrade/replay challenge); `OWNER-DECISION-0006` (below-floor posture).

### 1.1 The floor rule is now stated over the ingress set, not over the word `rollback`

**Prior text.**

- `ARCH-0003.yaml:86-87` (§7, heading "Rollback, freshness and revocation"): "Clients persist the highest valid
  root/metadata versions and minimum secure release they have observed. **Rollback below those floors is refused.**"
- `00-ARCHITECTURE.md:32` (§"Security objective"): "**rollback below known signed floors is refused**".
- `00-ARCHITECTURE.md:104` (§"Freshness and revocation"): "A signed minimum secure release prevents unsafe
  **rollback** while preserving historical authenticity."

**Corrected text.**

- `ARCH-0003.yaml:110` — §7 retitled **"Ingress floors, freshness and revocation"**. `ARCH-0003.yaml:112-117`: "Those
  floors are a property of the machine, not of one operation: no privileged lifecycle ingress — init, adopt, update,
  reinstall, rollback or recovery — may place the machine on a release below its protected local high-water or below
  the signed minimum secure release. The rule is scoped over the ingress set; `rollback` is the name of one governed
  ingress, not the name of the rule, and the floor check is part of the one verification policy of section 3 that
  every ingress calls."
- `00-ARCHITECTURE.md:94-96` — new subsection **"Signed floors bind every ingress"** under §"Lifecycle ingress
  invariant", stating the same rule over the six named ingresses.
- `00-ARCHITECTURE.md:32` — the security objective now reads "no lifecycle ingress places the machine on a release
  below its protected high-water or the signed minimum secure release, except under the explicitly authorised,
  recorded and marked break-glass recovery mode below".
- `00-ARCHITECTURE.md:136` — "prevents unsafe **downgrade at every ingress, not only at `rollback`**".

**R1 verifier can now test.** For each of the six ingresses independently: offer a validly signed release below the
protected high-water, and below the signed minimum secure release, and require a typed refusal. The test no longer
depends on which ingress name appears in the guarantee sentence.

### 1.2 The `recovery` ingress's second admissible object is qualified: intact ≠ admissible

**Prior text.** `00-ARCHITECTURE.md:80`, `recovery` row: "authenticated recovery target **or installed valid recovery
path** | bounded local recovery authority | restore one complete valid state".

**Corrected text.**

- `00-ARCHITECTURE.md:90`, `recovery` row: "authenticated recovery target, **or an installed complete local copy shown
  intact by D-0007 records and previously authenticated by this machine — in both cases not below the
  security/high-water floor** | bounded local recovery authority; **below floor only under break-glass** | restore one
  complete valid state **at or above floor, or a marked `DEGRADED — RECOVERY ONLY` state**".
- `00-ARCHITECTURE.md:98`: "Local installed-integrity evidence establishes that a local copy is *intact*, never that it
  is *admissible*. D-0007's payload ↔ `KERNEL_MANIFEST.json` ↔ `framework.lock` chain detects post-install tampering;
  per OWNER-DIRECTIVE-0004 it is not a first-install authenticity root, and it is not a floor check. Where no current
  metadata is reachable, the authenticity of an installed local recovery path comes from this machine's own protected
  record of the release identity it previously verified and installed — not from the manifest, the lock, the repository
  or mutually consistent files shipped with that copy. Admissibility is still the floor check."
- `ARCH-0003.yaml:120-129` — the same distinction in the architecture record: the D-0007 records "establish only that
  the local copy is unmodified. They do not establish that it is authentic, and they do not establish that it is
  admissible."

**Why authenticity is drawn from protected local state.** `OWNER-DECISION-0006` requirement 1 requires an authentic
release, and requirement 10 requires recovery to remain possible with no network access. Both hold only if offline
authenticity comes from something the machine already holds. The architecture therefore names the machine's own
protected record of the previously verified release identity — which the candidate already maintains
(`ARCH-0003.yaml` §3 step 8, protected local state) — and explicitly excludes the manifest, the lock, the repository
and files shipped with the copy, preserving OWNER-DIRECTIVE-0004's non-circularity rule. No new record type, format or
mechanism is specified; making that record durable is R1.

**R1 verifier can now test.** Present a locally complete, self-consistent installation whose D-0007 records all verify
but whose release identity is below the floor, and require refusal outside break-glass; and present one whose release
identity was never recorded as verified by this machine, and require that D-0007 self-consistency alone does not admit
it.

### 1.3 The below-floor case is stated per `OWNER-DECISION-0006`: break-glass, authorised and recorded

**Prior text.** None. The architecture was silent, which is exactly why the finding recorded two opposite
implementations as consistent with it.

**Corrected text.** `ARCH-0003.yaml:131-158` — new §7.1 "Below-floor break-glass recovery";
`00-ARCHITECTURE.md:100-114` — new subsection "Below-floor break-glass recovery". Below-floor recovery is refused by
default and admissible only as an explicit owner-authorised emergency recovery mode. The ten binding requirements are
mapped one by one in the table below.

**R1 verifier can now test.** That below-floor recovery fails closed without break-glass authority; that the authority
cannot be produced from repository content, environment, caller fields, plugins or model output; that entry writes the
durable record; that the marking is present and reported; that each forbidden operation is refused while marked; and
that the marking clears only after an at-or-above-floor authenticated release is installed and verified.

### 1.4 The revoked-binary allowance is made consistent

**Prior text.** `ARCH-0003.yaml:91`: "A known revoked binary is limited to inspection, export, **recovery** and
uninstall and cannot perform privileged governance work." `00-ARCHITECTURE.md:109`: "A known-revoked binary is limited
to inspection, export, **recovery** and uninstall."

**Corrected text.**

- `ARCH-0003.yaml:162-168` (§7.2): "A known revoked binary is limited to inspection, export, diagnosis, repair,
  uninstall and **participation in restoring an admissible release** … That recovery allowance is a path back to an
  admissible state, not an authority to re-establish the revoked release itself: a revoked or below-floor release is
  not an admissible recovery object under the floor check, and placing the machine back onto one requires the
  break-glass authorisation of section 7.1, **which a revoked binary cannot issue to itself** and which leaves the
  machine marked `DEGRADED — RECOVERY ONLY` with privileged governance work withheld."
- `00-ARCHITECTURE.md:142` — the same statement in the freshness bullet list.

This closes step 6 of the finding's counterexample, in which the restored revoked binary could re-invoke the same
ingress on its own authority.

**R1 verifier can now test.** That a revoked release is rejected as a recovery object under the ordinary floor check,
and that a running below-floor or revoked binary cannot originate its own break-glass entry.

### 1.5 `OWNER-DECISION-0006` requirement-by-requirement map

| # | Binding requirement | Where it is now stated |
|---|---|---|
| 1 | The recovery release must still be an authentic Governance OS release; no arbitrary or unsigned code | `ARCH-0003.yaml:138-140` ("Break-glass relaxes the floor check only; it never relaxes the authenticity check and never admits arbitrary or unsigned code"); `00-ARCHITECTURE.md:104` bullet **Authentic release only**; offline authenticity basis at `ARCH-0003.yaml:124-129` and `00-ARCHITECTURE.md:98` |
| 2 | Authority from an owner-controlled local/out-of-band mechanism, not manufacturable by repository content, environment variables, caller fields, plugins or model output | `ARCH-0003.yaml:140-144`; `00-ARCHITECTURE.md:105` bullet **Non-manufacturable authority** (also excludes self-authorisation by a below-floor or revoked binary) |
| 3 | Durable record on entry: machine identity, current floor/high-water, recovery release identity, reason, timestamp/evidence | `ARCH-0003.yaml:144-147`; `00-ARCHITECTURE.md:107` bullet **Durable entry record** |
| 4 | Explicit marking `DEGRADED — RECOVERY ONLY` | `ARCH-0003.yaml:147-149`; `00-ARCHITECTURE.md:108` bullet **Explicit marking**; also in the `recovery` ingress row (`00-ARCHITECTURE.md:90`) and the revoked-binary bullet (`00-ARCHITECTURE.md:142`) |
| 5 | Permitted activities: inspection; backup/export; diagnosis; repair; uninstall/reinstall; restoration of an authenticated release | `ARCH-0003.yaml:149-151`; `00-ARCHITECTURE.md:109` bullet **Permitted while below floor** |
| 6 | Forbidden: normal privileged operation; creating/approving Human Gates; release certification; trust-policy mutation; privileged plugin/profile acquisition; lowering or resetting floor/high-water; treating the release as current or fully trusted | `ARCH-0003.yaml:151-156`; `00-ARCHITECTURE.md:110` bullet **Refused while below floor** |
| 7 | Exit condition: an authenticated release at or above the signed minimum secure version is installed and verified | `ARCH-0003.yaml:154-156`; `00-ARCHITECTURE.md:112` bullet **Exit condition** |
| 8 | The security floor itself is not lowered | `ARCH-0003.yaml:153-154` ("never lowered, reset or forgotten … the mode records that the machine is knowingly operating beneath them, it does not move them"); `00-ARCHITECTURE.md:111` bullet **The floor is not lowered**; `00-ARCHITECTURE.md:141` ("break-glass does not lower, reset or forget it") |
| 9 | Ingress consistency: the floor rule governs `recovery`, `rollback` and every other backward-capable privileged ingress | `ARCH-0003.yaml:112-117` (§7, all six ingresses named); `00-ARCHITECTURE.md:94-96` ("Signed floors bind every ingress"); `00-ARCHITECTURE.md:32`; `00-ARCHITECTURE.md:136` |
| 10 | Network/GitHub access is not the sole break-glass authority; recovery remains possible without it | `ARCH-0003.yaml:143-144` ("Network or repository-hosting reachability is not that authority and is not a precondition of it: recovery must remain possible with no network or code-hosting access"); `00-ARCHITECTURE.md:106` bullet **Works without network**; offline authenticity basis at `00-ARCHITECTURE.md:98` |

**Deliberately not specified**, per `OWNER-DECISION-0006` and HO-0024: the break-glass authority's implementation,
storage format, identifiers, operator/CLI surface and tests. `ARCH-0003.yaml:157-159` and
`00-ARCHITECTURE.md:114` state that those are R1 and that the listed properties are the R0-normative part.

---

## CD-R0-2 — closes `SRR-R0-M1` (MEDIUM)

**Finding.** No time/clock assumption or non-guarantee was declared, although the whole expiry/freshness/stale-honesty
model is evaluated against one. Frozen R0 items **12** (local OS/admin/**time**/network assumptions and explicit
non-guarantees) and **10** (explicit stale, expired and offline states without false revocation knowledge) were
recorded as not satisfied, the latter because the honesty claim was untestable without a declared basis.

**Normative sources.** Frozen boundary R0 items 12 and 10, and R0 acceptance clause 1 ("explicit, internally
consistent and testable at later gates"); Contract v3 §"Evidence freshness" and §A2 bullet 10.

### 2.1 The local time source is named and placed

**Prior text.** `ARCH-0003.yaml:28-32`: "R0 assumes the local OS, administrator and bootstrap installation boundary
are uncompromised." `00-ARCHITECTURE.md:36-43`: six environment bullets, none naming time. A case-insensitive sweep of
all seven authoritative inputs for `clock|time|wall|NTP` returned zero matches (AR-0023 probe PR-3).

**Corrected text.**

- `ARCH-0003.yaml:46-49`: "R0 assumes the local OS, administrator, bootstrap installation boundary **and local time
  source** are uncompromised. The local clock is declared **inside the trusted local boundary**, on the same side of
  the line as the OS and administrator and **not on the untrusted network side**; no signed, attested, monotonic or
  network-supplied time is assumed, required or provided."
- `00-ARCHITECTURE.md:41`: new environment bullet — "the local time source treated as inside the trusted local
  boundary, on the OS/administrator side of the line rather than the untrusted network side".

This answers the question the finding said a reader could not answer: the clock is on the trusted side, with the OS
and administrator, not on the network side.

### 2.2 The non-guarantee is stated in the existing register

**Prior text.** `ARCH-0003.yaml:30-32` listed four non-guarantees; none concerned time. `00-ARCHITECTURE.md` had no
non-guarantee list at all, only the six-bullet environment.

**Corrected text.**

- `ARCH-0003.yaml:51-58`: "It does not claim correct expiry, staleness or currency determinations when the local clock
  is materially wrong: expiry, staleness and currency are evaluated by comparing signed expiry fields to that clock, so
  a clock set behind may accept expired metadata as unexpired and report currency as current when it is not, and a
  clock set ahead may treat current metadata as expired and refuse trust-changing operations the profile would
  otherwise permit. Neither case lowers a signed floor, admits an unauthorised release or breaks the verified-byte
  binding; the failure is confined to freshness." The same passage also adds "and it claims no knowledge of future
  revocations that do not yet exist".
- `00-ARCHITECTURE.md:46-51`: a new explicit non-guarantee list in the same register as the environment bullets,
  carrying both clock-direction cases, the unseen-and-future-revocation limit, and the bound that neither clock case
  lowers a floor, admits an unauthorised release or breaks the verified-byte binding.
- `00-ARCHITECTURE.md:53`: "No trusted-time service, attested time, monotonic-time source, signed-time floor or
  clock-independent freshness mechanism is assumed, required or provided by this profile. Expiry durations remain
  R1/R2 profile parameters." This is stated so the excluded mechanisms cannot be read back in as implied requirements.

### 2.3 The currency-honesty claim is made conditional

**Prior text.** `00-ARCHITECTURE.md:32`: "Given an authentic bootstrap verifier/root set and an uncompromised local
OS/admin boundary, … **stale/unknown currency is reported honestly**". `ARCH-0003.yaml:92-93`: "Offline clients report
currency stale/unknown and never claim knowledge of unseen revocations" — unconditional.

**Corrected text.**

- `00-ARCHITECTURE.md:32`: the premise now reads "Given an authentic bootstrap verifier/root set, an uncompromised
  local OS/admin boundary **and a local time source inside that boundary**, …", and the claim reads "stale/unknown
  currency is reported honestly **against that declared time source**".
- `ARCH-0003.yaml:170-175` (§7.2): "**Given an authentic bootstrap verifier/root set, an uncompromised local OS/admin
  boundary and a local time source inside that boundary as declared in section 1**, offline clients report currency
  stale/unknown and never claim knowledge of unseen revocations. Expiry, staleness and currency are determined against
  that declared local clock; the honesty claim holds while the clock is materially correct, and section 1 states what
  is and is not promised when it is not."
- `00-ARCHITECTURE.md:140`: the same conditional form added as a bullet in §"Freshness and revocation".

**R1 verifier can now test.** With the clock held correct: expired metadata is reported expired, unseen-revocation
knowledge is never claimed, and currency is `STALE`/`UNKNOWN` when no newer metadata has been received. With the clock
set behind or ahead: the declared non-guarantee defines the expected degradation, and the verifier can assert the
bound that still holds — no floor lowered, no unauthorised release admitted, verified-byte binding intact. The premise
is now defined, so both the passing and the failing test have a stated basis.

**Not done, by instruction.** No trusted-time service, monotonic-time source, time attestation, signed-time floor,
roughtime or clock-independent freshness mechanism was introduced, and no expiry duration was selected. Stronger-
assurance proposal 1 in `20-LATER-LIFECYCLE-CONDITIONS.md` remains unadopted and non-binding.

---

## Lineage bookkeeping in `ARCH-0003.yaml`

- `status: PROVISIONAL`, `in_effect: false`, `human_approved: false` and `proposal_state: R0_REVIEW_CANDIDATE` are
  unchanged. This is a corrected R0 candidate, not an accepted architecture.
- `updated` already carried `"2026-09-17"`, which is the date of this correction; it is therefore unchanged in value.
- Added `correction_state: R0_CORRECTION_1_APPLIED_PENDING_FRESH_R0_RE_REVIEW`.
- Added a `corrections:` list with one entry `R0-CORRECTION-1`, recording the corrected verdict/run/commits, the
  findings closed, the correction delta, the owner inputs, this record's path, the body sections changed and
  `self_graded: false`.
- `governed_by`, `depends_on`, `affects`, `tags`, `review_state` and `approval_state` are unchanged.

## What was deliberately not changed

- `01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` — re-hashed after the correction and byte-identical
  (`70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1`).
- `02-OP-1-OP-16-DISPOSITION.md`, `03-TRANSITION-MAP.md`, `D-0009`, `D-0007`, `D-0008`, `ARCH-0002`, every file under
  `*-review*/`, `release/verification/**`, `release/releases/**`, and all product source, runtime, kernel, CLI,
  capabilities, migrations and tests.
- `SRR-R0-L1`…`SRR-R0-L9` — none is routed into this correction. `SRR-R0-L6` is deferred to R1 and `SRR-R0-L7` is
  closed, both by `OWNER-DECISION-0005`; `SRR-R0-L8` (the traceability table maps 11 of 14 R0 items) is **not** fixed
  here — no rows were added. The two existing rows for R0 items 8 and 12 were re-pointed only because the sections
  they cite changed under this correction.
- No RoT-1 Revision 8; no resumption of CP-1; no new architecture lineage; no implementation.

## Self-assessment boundary

This role corrected the candidate and recorded what changed. It did not evaluate whether the corrections satisfy R0,
did not re-run the R0 item disposition, and issues no acceptance token. `GATE-R0-ARCH-ACCEPT` remains open and is
decided by a fresh independent R0 reviewer of this corrected candidate.

No `NEW_OWNER_DECISION_REQUIRED` item was surfaced by this correction: `OWNER-DECISION-0006` supplied the one owner
trade-off CD-R0-1 was blocked on, and CD-R0-2 required none.
