# 00 — Fresh independent R0 architecture re-review of the corrected Signed Release Root v1

| Field | Value |
|---|---|
| Run | `AR-0025` |
| Role | fresh independent R0 architecture reviewer (`r0-architecture-reviewer`) |
| Handoff | `HO-0025-srr1-r0-re-review.md` |
| Gate | `GATE-R0-ARCH-ACCEPT` |
| Reviewed worktree HEAD | `2b36b440915f0052d92153748cea914846955418` |
| Review branch | `phase1/srr1-r0-review-2` |
| Corrected candidate | `D-0009` / `ARCH-0003` / `release/root-of-trust/signed-release-root-v1/` |
| Pre-correction commit (diff base) | `73227a1594265743b18eb7115394d639e6c659a2` |
| Correction commit | `29516f8` (merged at `d34478a`) |
| Prior verdict corrected | `AR-0023` `ROT_ARCHITECTURE_REJECTED_R0` (work commit `2dc08c2`) |
| Date | 2026-09-17 |

# VERDICT

## `ROT_ARCHITECTURE_ACCEPTED_R0`

The corrected architecture satisfies the frozen R0 acceptance rule in
`01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`. Both AR-0023 blockers are **CLOSED**.
All fourteen frozen R0 items are explicit, internally consistent and testable at later
gates. No CRITICAL or HIGH defect falsifies an R0 normative guarantee, and no unresolved
MEDIUM requires an architecture change to meet one.

Acceptance is of the **architecture and its stated assumptions only**. It does not
activate implementation, does not accept any R1 candidate, certifies no release, and
changes nothing about `D-0007`, `D-0008`, `ARCH-0002` or the frozen boundary.

## Independence statement

I did not author this architecture, the `AR-0024` correction, or the `AR-0023` review. I
am the sole issuer of this verdict. I re-executed both prior blockers against the corrected
text rather than accepting the correction record's account of them, and I authored sixteen
fresh held-out attacks of my own. No helper session, subagent or external agent was spawned
or consulted; there is no delegation to disclose. The product owner was not contacted. The
one `NEW_OWNER_DECISION_REQUIRED` item I surfaced is recorded for the orchestrator to route
and is **not** a condition of this verdict.

# 1. Input verification — no STOP condition

All seven digests pinned by `HO-0025` were recomputed in the review worktree before any
reliance was placed on the corresponding file. **All seven match exactly.** Full output in
`evidence/REVIEWED-CONTENT-DIGESTS.txt`; summary at `evidence/PROBES.md` NR-1.

Contract v3 was read only from the hash-verified file at the repository root. No contract
text was reconstructed from memory or from generated documentation.

`D-0008`, `ARCH-0002` and RoT-1 revisions 1–7 were treated as **evidence only**, mined for
attack shapes, and created no R0 requirement in this review.

# 2. Disposition of the two prior blockers

## `SRR-R0-H1` (HIGH) — **CLOSED**

*Signed rollback floors scoped only to `rollback`; the `recovery` ingress admits a
floor-free, non-metadata-authenticated restore.*

Re-executed, not taken on trust. AR-0023's probe PR-5 was rerun in full (`evidence/PROBES.md`
NR-4): every one of the five floor statements it cited has been replaced, and the
counterexample's six steps are each now blocked by named architecture text.

Against AR-0023's own counterexample, step by step:

| AR-0023 step | Corrected text | Status |
|---|---|---|
| 4. `recovery` selects "installed valid recovery path" `v4`, validated by D-0007 self-consistency | `00-ARCHITECTURE.md:98` — installed-integrity evidence establishes *intact*, "never that it is *admissible*… and it is not a floor check"; `ARCH-0003.yaml:120-124` separates intact / authentic / admissible | blocked |
| 5. Nothing consults the floor because the rule names only `rollback` | `00-ARCHITECTURE.md:96` and `ARCH-0003.yaml:113-116` — the rule is stated over all six ingresses and bound to "the single verification policy every ingress calls" | blocked |
| 6. Revoked `v4` restored; the revoked binary may re-invoke the same ingress | `ARCH-0003.yaml:163-168` — "a revoked or below-floor release is not an admissible recovery object under the floor check", and re-entry "requires the break-glass authorisation… which a revoked binary cannot issue to itself" | blocked |
| — the authenticity source for an offline restore | `00-ARCHITECTURE.md:98` — "this machine's own protected record of the release identity it previously verified and installed — not from the manifest, the lock, the repository or mutually consistent files shipped with that copy" | supplied, and non-circular (NA-8) |

The owner's trade-off is stated rather than left to an implementer: below-floor recovery is
refused by default and admissible only as an explicit owner-authorised break-glass mode with
eight R0-normative properties. The availability half of AR-0023's trade-off — a machine whose
only complete local state is below its own floor — is answered, which was the point of
`OWNER-DECISION-0006`.

**Not a residual.** Fresh attacks NA-1 through NA-9 were run against the replacement text and
none reopens it.

## `SRR-R0-M1` (MEDIUM) — **CLOSED**

*No time/clock assumption or non-guarantee declared, although the entire
expiry/freshness/stale-honesty model is evaluated against one.*

AR-0023's probe PR-3 returned **zero matches** for `clock|time|wall|NTP` across the
candidate. The same sweep on the corrected text returns **fourteen** (`evidence/PROBES.md`
NR-3). All three parts of CD-R0-2 are satisfied in architecture text:

1. **The time source is named and placed.** `ARCH-0003.yaml:47-49`; `00-ARCHITECTURE.md:41` —
   the local clock is declared inside the trusted local boundary, "on the OS/administrator
   side of the line rather than the untrusted network side". This answers the precise
   question AR-0023 said a reader could not resolve, and it resolves the A-07 freeze/replay
   reading.
2. **The non-guarantee is stated, in both directions.** `00-ARCHITECTURE.md:51`;
   `ARCH-0003.yaml:53-58` — clock behind may accept expired metadata as unexpired and report
   currency as current; clock ahead may refuse operations the profile would permit.
3. **The honesty claim is conditional.** `00-ARCHITECTURE.md:32`, `:140`;
   `ARCH-0003.yaml:170-174` now carry the same "Given an authentic bootstrap verifier/root
   set, an uncompromised local OS/admin boundary and a local time source inside that
   boundary…" premise the rest of the document uses, so an R1 verifier can write a test with
   a defined premise.

The correction also respected the owner's constraint in `OWNER-DECISION-0006`: it was **not**
broadened into another trust-state protocol. `00-ARCHITECTURE.md:53` declares affirmatively
that no trusted-time service, attested time, monotonic source, signed-time floor or
clock-independent freshness mechanism is assumed, required or provided. Expiry durations
remain R1/R2 parameters.

I tested the correction's own safety claim — "Neither case lowers a signed floor, admits an
unauthorised release or breaks the verified-byte binding" — rather than accepting it
(`evidence/PROBES.md` NA-10). **It holds**, because both floors are anchored to monotonic
version state rather than to time: `00-ARCHITECTURE.md:135` and `:141` are clock-independent,
and expiry confers no authorisation. NA-11 separately confirms that no clock manipulation can
manufacture break-glass entry.

**Not a residual.**

# 3. Fresh held-out attacks authored by this review

Sixteen attacks, in `evidence/PROBES.md` NA-1…NA-16. Summary:

| # | Attack | Result |
|---|---|---|
| NA-1 | Does break-glass relax more than the floor check? | PASS — confined to admissibility |
| NA-2 | Can repository content, env vars, caller fields, plugins or model output manufacture break-glass authority? | PASS — all five excluded, plus self-authorisation |
| NA-3 | Can a revoked binary re-establish itself via the recovery allowance? | PASS — closed at three points |
| NA-4 | Is network/code-hosting reachability a precondition of recovery? | PASS — owner requirement 10 met with a stated basis |
| NA-5 | Deadlock — can a below-floor machine actually escape? | PASS — restoration explicitly permitted; no gate needed |
| NA-6 | Is the `DEGRADED — RECOVERY ONLY` token byte-identical to the owner's? | PASS — exact at all five sites |
| NA-7 | Can "intact" be read as "admissible"? | PASS — three distinct predicates, three sources |
| NA-8 | Is the offline authenticity basis circular? | PASS on circularity; precision point → `SRR2-R1-C2` |
| NA-9 | Does the floor rule reach `init`/`adopt`/`update`/`reinstall`? | PASS — all six named in three places |
| NA-10 | Can a wrong clock lower a signed floor? | PASS — floors are version-anchored, not time-anchored |
| NA-11 | Can a wrong clock enable break-glass entry? | PASS — authority is not time-derived |
| NA-12 | Does the break-glass marking survive until **both** floors are met? | Ambiguity found → `SRR2-R1-C1`, R1, non-blocking |
| NA-13 | Is the high-water durable across a normal uninstall? | PASS on stated text → `SRR2-R1-C3`, R1, LOW |
| NA-14 | Did the correction weaken any previously satisfied R0 item? | PASS — no weakening |
| NA-15 | Did the correction smuggle later-lifecycle scope into R0? | PASS — no smuggling |
| NA-16 | Are the two re-pointed traceability rows accurate? | PASS — both verify |

The two attacks that produced findings, NA-12 and NA-13, are **new**, not residuals of
`SRR-R0-H1` or `SRR-R0-M1`. Neither blocks: see `10-BLOCKING-FINDINGS.md` and
`20-LATER-LIFECYCLE-CONDITIONS.md`.

# 4. `OWNER-DECISION-0006` — all ten requirements confirmed in architecture text

Verified against `ARCH-0003.yaml` and `00-ARCHITECTURE.md` directly, **not** against the
correction record's map. The correction record is a map; the architecture is the artifact.
Every requirement is present in both documents.

| # | Owner requirement | In architecture text | Confirmed |
|---|---|---|---|
| 1 | Authentic Governance OS release only; no arbitrary or unsigned code | `ARCH-0003.yaml:138-140`; `00-ARCHITECTURE.md:104` | **yes** |
| 2 | Owner-controlled local/out-of-band authority; not manufacturable by repository content, environment variables, caller fields, plugins or model output | `ARCH-0003.yaml:140-143`; `00-ARCHITECTURE.md:105` — all five named; architecture adds exclusion of self-authorisation by a below-floor or revoked binary | **yes (superset)** |
| 3 | Durable entry record: machine identity, current floor/high-water, recovery release identity, reason, timestamp/evidence | `ARCH-0003.yaml:143-145`; `00-ARCHITECTURE.md:107` — all five fields | **yes** |
| 4 | Explicit marking `DEGRADED — RECOVERY ONLY` | `ARCH-0003.yaml:146`, `:168`; `00-ARCHITECTURE.md:90`, `:108`, `:142` | **yes — byte-identical token, NA-6** |
| 5 | Permitted: inspection; backup/export; diagnosis; repair; uninstall/reinstall; restoration of an authenticated release | `ARCH-0003.yaml:149-151`; `00-ARCHITECTURE.md:109` — all six | **yes** |
| 6 | Forbidden: normal privileged operation; creating/approving Human Gates; release certification; trust-policy mutation; privileged plugin/profile acquisition; lowering or resetting floor/high-water; treating the release as current or fully trusted | `ARCH-0003.yaml:149-155`; `00-ARCHITECTURE.md:110` — all seven | **yes** |
| 7 | Exit: an authenticated release at or above the signed minimum secure version is installed and verified | `ARCH-0003.yaml:154-155`; `00-ARCHITECTURE.md:112` | **yes** (see `SRR2-R1-C1` on its interaction with the high-water) |
| 8 | The security floor itself is not lowered | `ARCH-0003.yaml:152-154`; `00-ARCHITECTURE.md:111`, `:141` | **yes** |
| 9 | Ingress consistency across `recovery`, `rollback` and every backward-capable ingress | `ARCH-0003.yaml:112-117`; `00-ARCHITECTURE.md:32`, `:94-96`, `:136` | **yes** |
| 10 | GitHub/network is not the sole authority; recovery remains possible without network access | `ARCH-0003.yaml:143-144`; `00-ARCHITECTURE.md:106`, with the offline authenticity basis at `:98` | **yes** |

Requirement 10 was checked specifically as `HO-0025` task 3 directs: recovery remains
possible with no network or code-hosting access, and the architecture supplies a
no-current-metadata authenticity basis rather than merely asserting the availability
property (NA-4).

The break-glass **mechanism** — storage format, operator surface, identifiers, tests — is
correctly left to R1 (`ARCH-0003.yaml:157-158`; `00-ARCHITECTURE.md:114`), with the eight
properties marked R0-normative. That matches `OWNER-DECISION-0006`'s own scoping.

# 5. Scope discipline of the correction

Verified mechanically (`evidence/PROBES.md` NR-2, NA-14, NA-15).

- **Stayed inside CD-R0-1 and CD-R0-2.** The correction commit touched exactly three paths:
  the two architecture documents named by the delta, plus its own new correction record.
- **Weakened nothing previously satisfied.** Every diff hunk was read line by line. The only
  deletions are five superseded floor sentences and three superseded freshness bullets, each
  replaced by a strictly stronger statement. The rewritten security objective widens scope
  from one ingress to six; its single exception is the owner's own decision, constrained by
  eight stated properties.
- **Routed no later-lifecycle condition into R0.** `SRR-R0-L1`…`L9` are untouched.
  `SRR-R0-L6` (owner-deferred) and `SRR-R0-L7` (owner-closed) were correctly left out, as
  `OWNER-DECISION-0005` directed. No production ceremony, DDC, supplier-independence,
  reproduction-quorum, multi-source-first-contact or Gate W/G6 requirement was introduced.
- **Historical and governing records preserved.** Blob-identity comparison confirms the frozen
  boundary, `02-OP-1-OP-16-DISPOSITION.md`, `03-TRANSITION-MAP.md`, `D-0009`, `D-0007`,
  `D-0008`, `ARCH-0002`, Contract v3, `OWNER-DIRECTIVE-0004` and all three AR-0023 evidence
  files are byte-identical. `D-0007` remains `status: ACTIVE`. `D-0008` and `ARCH-0002` remain
  `PROVISIONAL` / `PROPOSED` / `in_effect: false`. No product source was touched, and no
  implementation exists.
- **Lineage bookkeeping is honest.** `ARCH-0003.yaml` still carries `status: PROVISIONAL`,
  `in_effect: false`, `human_approved: false`, `proposal_state: R0_REVIEW_CANDIDATE`, and the
  new `corrections` entry records `self_graded: false` and asserts no acceptance. The
  correction record's §"Self-assessment boundary" correctly disclaims grading itself.

# 6. Disclosed judgement call — `SRR-R0-L8` re-points verified

AR-0024 disclosed that it did not fix `SRR-R0-L8` (the R0 traceability table maps 11 of 14
items) but re-pointed two existing rows whose target sections moved. **Both re-points are
accurate** (`evidence/PROBES.md` NA-16). All five cited section headings exist verbatim and
each contains the material the row claims. The row count is unchanged at eleven, so the
disclosure that `SRR-R0-L8` was not fixed is itself accurate. `SRR-R0-L8` is carried forward
at unchanged INFO severity; frozen R0 items 13 and 14 remain covered in body text.

# 7. Per-item disposition of the fourteen frozen R0 items

| # | Frozen R0 item | Where | Disposition |
|---|---|---|---|
| 1 | Pre-existing platform/admin bootstrap assumption | `ARCH-0003.yaml` §5, §1; `00-ARCHITECTURE.md` Declared environment + Bootstrap trust-domain row | **SATISFIED** — uncontested at AR-0023, unchanged, not reopened |
| 2 | Signed root, delegation and release/targets metadata | `ARCH-0003.yaml` §3, §4; `00-ARCHITECTURE.md` Metadata roles | **SATISFIED** — unchanged |
| 3 | Binding of release identity, exact payloads and migrations | `ARCH-0003.yaml` §4 `:83-85`; `00-ARCHITECTURE.md:77` | **SATISFIED** — unchanged |
| 4 | Key delegation, rotation and revocation semantics | `ARCH-0003.yaml` §4 `:89-91`; `00-ARCHITECTURE.md` Metadata roles, Freshness and revocation | **SATISFIED** — `SRR-R0-L1` (R1) carried |
| 5 | One verification policy across init, adopt, update, reinstall, rollback and recovery | `ARCH-0003.yaml:73`, §7 `:112-117`; `00-ARCHITECTURE.md:83-96` | **SATISFIED — strengthened.** The floor check is now explicitly part of the one policy every ingress calls |
| 6 | Verified-byte/use binding | `ARCH-0003.yaml` §6 `:101-107`; `00-ARCHITECTURE.md` Transaction invariant | **SATISFIED** — unchanged |
| 7 | Private staging, atomic commit, crash-safe outcome | same | **SATISFIED** — unchanged; `SRR-R0-L5` (R1) carried |
| 8 | Signed rollback floors and protected local high-water | `ARCH-0003.yaml` §7, §7.1; `00-ARCHITECTURE.md:94-114`, `:135-142` | **SATISFIED — was `SRR-R0-H1`, now closed.** Floors bind all six ingresses; below-floor case decided per owner. `SRR2-R1-C1` (R1) and `SRR2-R1-C3` (R1) carried, neither blocking |
| 9 | Local authority/Human Gate and headless-policy boundaries | `ARCH-0003.yaml` §8; `00-ARCHITECTURE.md` Headless CI and multiple machines | **SATISFIED** — unchanged; `SRR-R0-L3` (R1) carried |
| 10 | Explicit stale, expired and offline states without false revocation knowledge | `ARCH-0003.yaml` §7.2; `00-ARCHITECTURE.md:131-142` | **SATISFIED — strengthened.** Adds "no knowledge of future revocations that do not yet exist" and a declared freshness basis |
| 11 | Separation of authenticity, installed integrity, build provenance, certification, project policy, plugin/retrieval trust | `00-ARCHITECTURE.md` Trust-domain boundaries; `ARCH-0003.yaml` §2, §9 | **SATISFIED — strengthened.** Intact / authentic / admissible are now three distinct predicates (NA-7); `SRR-R0-L6` owner-deferred to R1 |
| 12 | Local OS/admin/time/network assumptions and explicit non-guarantees | `ARCH-0003.yaml` §1 `:45-58`; `00-ARCHITECTURE.md:34-53` | **SATISFIED — was `SRR-R0-M1`, now closed.** Time declared, placed, and given a two-directional non-guarantee |
| 13 | Preservation of the original Governance OS mission and Contract v3 capabilities | `00-ARCHITECTURE.md` Preservation of Governance OS; `ARCH-0003.yaml` §9, §11 | **SATISFIED** — unchanged; absent from the traceability table (`SRR-R0-L8`, INFO) |
| 14 | D-0007 remaining active; non-circular first-install authenticity supplied outside its manifest/lock | `D-0007` `status: ACTIVE` verified; `ARCH-0003.yaml` §5, §7, §11; `00-ARCHITECTURE.md:98` | **SATISFIED — strengthened.** OWNER-DIRECTIVE-0004's rule is now explicitly preserved at the one ingress that consults no metadata; basis verified non-circular (NA-8). `SRR2-R1-C2` (R1) carried, non-blocking |

**Fourteen of fourteen satisfied.** Five strengthened by the correction (items 5, 10, 11, 12,
14) plus item 8; none weakened.

# 8. Against the frozen R0 acceptance rule

| Acceptance clause | Assessment |
|---|---|
| every R0 item explicit, internally consistent and testable at later gates | **met** — §7 above; the one internal ambiguity found (`SRR2-R1-C1`) has a compliant reading already in the text and does not make any item untestable |
| no unresolved CRITICAL/HIGH defect that falsifies an R0 normative guarantee | **met** — none found; `SRR-R0-H1` closed |
| no unresolved MEDIUM that requires architecture change to meet an R0 guarantee | **met** — `SRR2-R1-C1` and `SRR2-R1-C2` are MEDIUM, and neither *requires* a change: each has a safe reading the architecture already supports |
| every carried R1/R2/R3 concern labelled with its correct lifecycle | **met** — `20-LATER-LIFECYCLE-CONDITIONS.md` |
| no private key, production ceremony or implementation required as evidence | **met** — none used or required; no implementation exists (NR-5) |
| the verdict identifies the exact reviewed Git commit and document hashes | **met** — HEAD `2b36b44…`; `evidence/REVIEWED-CONTENT-DIGESTS.txt` |

# 9. Items for the orchestrator to route

One `NEW_OWNER_DECISION_REQUIRED`, **not** a condition of this verdict and **not** a blocker:

- **`SRR2-R1-C1`** — does exit from `DEGRADED — RECOVERY ONLY` require a release at or above
  (a) the signed minimum secure release only, as `OWNER-DECISION-0006` requirement 7 states
  today, or (b) **both** that floor and the protected local high-water? Recommended R1 default
  pending an answer: the stricter reading, which is already supported by
  `00-ARCHITECTURE.md:96` and `:108` and fails safe. This review does not choose and does not
  author the clause.

# 10. Scope deviations and prohibitions

No scope deviation. No STOP condition. No implementation was written or authorised. No
replacement architecture and no further correction delta was authored. No RoT-1 Revision 8, no
CP-1 resumption, no change to `D-0007`, `D-0008` or `ARCH-0002`. No product source, frozen
boundary, prior review evidence or historical record was modified; the sole directory written
by this run is `release/root-of-trust/signed-release-root-v1-review-r0-2/`, plus
`AGENT_RUNS/AR-0025.report.yaml` in a separate commit. No session transcript or task-output
store was read. No user auto-memory was opened or written. The product owner was not contacted.

# 11. Recommended next action

Close `GATE-R0-ARCH-ACCEPT` as **passed** on `ROT_ARCHITECTURE_ACCEPTED_R0` and record
`ARCH-0003` as R0-accepted. `ARCH-0003` should remain `in_effect: false` and
`human_approved: false` until the product owner adopts it; R0 acceptance authorises no
implementation. Route `SRR2-R1-C1` to the owner as a bounded question, and carry
`SRR2-R1-C2`, `SRR2-R1-C3`, `SRR-R0-L1`…`L6`, `L8` and `L9` into the R1 planning input at
their labelled lifecycles.
