# 20 — Non-blocking later-lifecycle conditions, risks and proposals (AR-0023)

Nothing in this file blocks `GATE-R0-ARCH-ACCEPT`, and nothing here is routed into
`11-CORRECTION-DELTA.md`. Each item carries its lifecycle. Per the frozen boundary,
a reviewer may recommend stronger security but cannot promote it into a
requirement; items marked *stronger-assurance proposal* require explicit owner
adoption before they bind anything.

| id | lifecycle | class | severity | owner action |
|---|---|---|---|---|
| `SRR-R0-L1` | R1 | `NECESSARY-DERIVED` | MEDIUM | no |
| `SRR-R0-L2` | R1 | `NECESSARY-DERIVED` | LOW | no |
| `SRR-R0-L3` | R1 | `NECESSARY-DERIVED` | MEDIUM | no |
| `SRR-R0-L4` | R1 | `OWNER-ADDED-NORMATIVE` | MEDIUM | no |
| `SRR-R0-L5` | R1 | `IMPLEMENTATION-CHOICE` | LOW | no |
| `SRR-R0-L6` | R1/R2 | `NEW-OWNER-DECISION-REQUIRED` | MEDIUM | **yes** |
| `SRR-R0-L7` | R1 | `NEW-OWNER-DECISION-REQUIRED` | LOW | **yes** |
| `SRR-R0-L8` | INFO | `IMPLEMENTATION-CHOICE` | INFO | no |
| `SRR-R0-L9` | R2 | `LATER-QUALIFICATION/CERTIFICATION` | INFO | no |

---

## SRR-R0-L1 — R1 — Root succession/rotation acceptance semantics are imported by reference

**Source:** frozen boundary R0 item 4; Contract v3 A2 ("Signing keys/trust anchors
support rotation/revocation/recovery"). **Class:** `NECESSARY-DERIVED`.
**Original-baseline:** yes. **Owner-approved:** yes. **Claim affected:** none —
this is not a falsification.

`ARCH-0003.yaml` states that root metadata authorises rotation and revocation, sets
a 2-of-3 offline root, restricts snapshot/timestamp purpose, and makes metadata
versions monotonic. It does not restate how a client holding root version *N*
accepts root version *N+k* — the succession chain that makes rotation work for a
client that has been offline across one or more rotations. `ARCH-0003.yaml` §4
imports this by reference ("Use a mature TUF-style metadata model"), and the frozen
boundary defers library/algorithm selection to R1/R2 and does not enumerate
succession chaining, so this is not an R0 defect.

**R1 condition:** the implementation candidate must demonstrate root succession
against the selected mature library, including a client several rotations behind,
and must state the behaviour when the stored root is older than the publisher
retains. **Consequence if ignored:** rotation becomes untestable and a key
compromise cannot be recovered from in practice. **Cost:** none at R0.

## SRR-R0-L2 — R1 — Release channel is used as a scoping concept but is not a bound metadata field

**Source:** frozen boundary R0 item 3 (enumerates identity, payloads, migrations —
**not** channel). **Class:** `NECESSARY-DERIVED`. **Original-baseline:** no.
**Owner-approved:** n/a. **Claim affected:** none.

`00-ARCHITECTURE.md:123` scopes trust-changing CI automation "to the exact
operation/release channel", but the bound metadata fields
(`00-ARCHITECTURE.md:67`) are product identity, version, monotonic sequence,
supported target, digests, schema/migration identities, minimum secure release,
metadata version/expiry and optional evidence digests. Channel is not among them.
Because channel is not an enumerated R0 binding, this cannot block R0.

**R1 condition:** if more than one channel is ever published under the same
delegated release role, either bind channel in the authenticated metadata or
express channels as distinct delegations, so that the CI scoping rule is
enforceable rather than nominal. **Consequence if ignored:** a client pinned to a
stable channel could be served a validly signed release from another channel.

## SRR-R0-L3 — R1 — "Repository gate records remain requests" must be scoped to trust-changing operations

**Source:** frozen boundary R0 items 9 and 13; D-0007 trust class T2 ("governed
records under `spec/` (decisions, gates, CITs, reports)" are authoritative project
state written by the OS); Contract v3 L2/L3 and G2. **Class:** `NECESSARY-DERIVED`.
**Original-baseline:** yes. **Owner-approved:** yes. **Claim affected:** none at R0
under the narrow reading.

`ARCH-0003.yaml:97` states "Repository gate records remain requests", while
`00-ARCHITECTURE.md:122` states "CI may consume already authoritative Human Gate
decisions; an environment variable, job input or repository file cannot manufacture
one." Read narrowly — the sentence sits directly after "Interactive trust changes
use local administrator/Human Gate authority", and the authority for trust-changing
automation is the out-of-repository machine/workload policy — the two are
consistent and the rule is a *strengthening*, which D-0007 permits. Read broadly,
it would demote every governed gate record in `spec/` from T2 to a request and
damage a preserved Contract v3 capability.

**R1 condition:** the implementation must scope this rule explicitly to
trust-changing lifecycle operations, leaving ordinary Human Decision Gates
governed by D-0007/Contract v3 L2 unchanged. **Consequence if ignored:** either an
unintended weakening of trust-change authority or an unintended breakage of the
product's Human Gate surface.

## SRR-R0-L4 — R1 — Contract v3 A2 bullet 8 (trust modes vs certified production) is unaddressed, and currently vacuous

**Source:** `Governance_OS_Capability_Acceptance_Contract_v3.md` §A2
**[POST-VERIFICATION HARDENING]**, bullet 8: "Bootstrap/dev/test trust modes cannot
masquerade as certified production." **Class:** `OWNER-ADDED-NORMATIVE`.
**Original-baseline:** yes (A2 is in the owner-approved contract).
**Owner-approved:** yes. **Claim falsified:** **none** — see below.

Probe PR-4 found no dev/test/bootstrap trust mode in the candidate architecture and
none in the shipped 4.1.5 source (`runtime/`, `cli/`, `framework/`, `spec/`:
zero matches for `dev_mode|insecure|unsigned|test_mode|GOV_TRUST|GOV_DEV|
bootstrap_mode|trust_mode|allow_untrusted|skip_verify`). The architecture defines
exactly one trust mode, so nothing exists to masquerade and no candidate claim is
falsified. Two adjacent A2 concerns *are* already covered: the trust-domain table
states certification is "not automatic from a signature", and the R3 token
`STANDARD RELEASE — HIGH-ASSURANCE TOOLCHAIN PROFILE NOT CERTIFIED` gives an
explicit negative certification state. The masquerade vector via caller input is
also already closed by `ARCH-0003.yaml` §6/§8.

**R1 condition:** the obligation binds the moment any non-production trust anchor
or bootstrap profile is introduced (the architecture anticipates alternative
profiles "added later"). At that point the implementation must record the
authenticating trust anchor/profile identity in protected local state and report it
alongside the certification axis, so authenticity and certification remain two
visible axes rather than one. **Consequence if ignored:** a development-rooted
install becomes indistinguishable from a production-rooted one.

## SRR-R0-L5 — R1 — High-water/journal durability ordering relative to atomic commit

**Source:** frozen boundary R0 items 7 and 8. **Class:** `IMPLEMENTATION-CHOICE`.
**Original-baseline:** no. **Owner-approved:** n/a. **Claim affected:** none — the
architecture explicitly assigns "specific filesystem primitives" to R1.

The transaction invariant orders "atomically commit one complete version" (5),
"verify the committed representation" (6), then "durably update journal and
high-water" (7). A crash between 5/6 and 7 leaves a correctly installed new version
with a lagging high-water, which could later admit an intermediate version the
machine has already passed.

**R1 condition:** demonstrate crash-safety across that window on supported
filesystems, including whether recovery re-derives the high-water from the
committed state. **Consequence if ignored:** a narrow, locally-reachable downgrade
window after an interrupted update.

## SRR-R0-L6 — R1/R2 — `NEW-OWNER-DECISION-REQUIRED` — Plugin/tool/skill first-acquisition source authenticity

**Source:** `ARCH-0003.yaml` §9 ("may additionally be distributed through delegated
signed targets" — permissive); Contract v3 F2 (provenance/hash pin, installation/
approval status), F3 (missing-tool acquisition), F4 **[POST-VERIFICATION
HARDENING]** (descriptor cannot self-authorise, bytes hash-bound, registration in
trusted OS state); frozen boundary R0 item 11, which scopes plugin/retrieval trust
as a **separate domain** from the release root. **Class:**
`NEW-OWNER-DECISION-REQUIRED`. **Original-baseline:** yes (F2/F3/F4).
**Owner-approved:** yes, as a separate domain. **Claim falsified:** none.

This is **not** an R0 defect: the owner deliberately separated plugin/retrieval
trust from the release root, and the candidate preserves F4 through D-0007. But it
leaves a real asymmetry worth an explicit owner answer. After SRR-1, Governance OS
release bytes are authenticated to a signed root, while plugin/tool/skill bytes
acquired through F3 are governed by approval, hash pin and kernel-owned
registration — that is, they are *self-consistently* pinned after acquisition
rather than authenticated to an independent root. That is the same shape as the
V-H3 argument, applied to a different domain, and it is only safe because the
declared envelope trusts the local administrator who approves the acquisition.

**Owner decision:** should Phase-1 plugin/tool acquisition be required to consume
delegated signed targets (turning `may additionally` into `must`, at the cost of
requiring the owner to sign every third-party tool), or remain governed-but-
unauthenticated-source under the trusted-admin envelope? I do not choose; I record
the trade-off for the orchestrator to route. **Consequence if unanswered:** R1
implements one of the two by default and the choice is never made explicitly.

## SRR-R0-L7 — R1 — `NEW-OWNER-DECISION-REQUIRED` — Offline/air-gapped install from a held authentic envelope is not designed

**Source:** Contract v3 §A2 bullet 10 ("Release verification works offline after
obtaining an authentic release envelope **where designed**"); frozen boundary R0
item 10. **Class:** `NEW-OWNER-DECISION-REQUIRED`. **Original-baseline:** yes.
**Owner-approved:** the "where designed" qualifier leaves it to the design.
**Claim falsified:** none — the candidate designs no offline install path, so the
qualifier is satisfied by omission.

Because expired/stale metadata blocks trust-changing operations, an air-gapped
machine holding a validly signed release envelope may be unable to install or
update it. The candidate preserves offline *recovery* through the "installed valid
recovery path" branch (see `SRR-R0-H1`, which also governs that branch), but not
offline *install*.

**Owner decision at R1:** whether the private/local profile needs an offline
install path at all, and if so what expiry policy applies to it. **Consequence if
unanswered:** an operational surprise on a disconnected machine rather than a
security defect.

## SRR-R0-L8 — INFO — R0 traceability table maps 11 of the 14 frozen R0 items

`00-ARCHITECTURE.md` §"R0 traceability" has eleven rows. The frozen boundary
enumerates fourteen R0 items. Items 13 (preservation of the original mission and
Contract v3 capabilities) and 14 (D-0007 remaining active; non-circular first-install
authenticity supplied outside its manifest/lock) are **covered in the body text** —
§"Preservation of Governance OS", the bootstrap trust-domain row, `ARCH-0003.yaml`
§11 and `03-TRANSITION-MAP.md` — but are absent from the table. Cosmetic;
completing the table would make the R0 self-check mechanical for future reviewers.

## SRR-R0-L9 — R2 — Release/targets threshold value and custody remain unspecified

Recorded for completeness only, and **not a defect**: the frozen boundary's
§"Not required at R0" explicitly excludes production signatures, custody ceremonies
and final library/algorithm selection, and `02-OP-1-OP-16-DISPOSITION.md` OP-1
assigns concrete custody evidence to R2. The 2-of-3 offline root target is stated;
the delegated release/targets threshold is not, and belongs at R2.

---

## Stronger-assurance proposals (not requirements, not conditions)

Recorded so the owner sees them, explicitly **not** adopted and **not** binding on
any gate. None of these appears in the correction delta and none should be treated
as a condition of R1 acceptance unless the owner adopts it.

1. A freshness signal that does not depend solely on the local clock — for example treating the newest validly observed signed timestamp as a monotonic lower bound on time, so that a backwards-set clock cannot make stale metadata appear current. This is a genuine hardening of `SRR-R0-M1`'s subject matter and is deliberately **excluded** from `CD-R0-2`, which asks only for the assumption to be declared.
2. Recording the authenticating root/profile identity in protected state and surfacing authenticity and certification as two explicit axes in operator-visible state, ahead of any second trust profile existing (`SRR-R0-L4` would then already be satisfied).
3. Expressing release channels as distinct TUF delegations rather than a metadata field, which would make `SRR-R0-L2` structurally enforceable.
