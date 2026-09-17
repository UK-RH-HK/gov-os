# Fresh independent R0 architecture review — Signed Release Root v1 (SRR-1)

| Field | Value |
|---|---|
| Run | `AR-0023` |
| Role | `r0-architecture-reviewer` (fresh, isolated; sole issuer of this verdict) |
| Active gate | `GATE-R0-ARCH-ACCEPT` |
| Candidate | D-0009 + ARCH-0003 + `release/root-of-trust/signed-release-root-v1/` |
| Reviewed worktree HEAD | `166ac4cff484160c7176e0ce15b23e59820074f2` (branch `phase1/srr1-r0-review`) |
| Reviewed-candidate commit | `5fd83583f36a32b045d3943dd5ee6f2c7a491822` (inputs byte-identical at HEAD — probe PR-2) |
| Owner rebase record | `2d78f6bf38f99ce1ff936eaf8b8b617e014441e7` |
| Acceptance rule applied | `01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md` §"R0 acceptance", sha256 `70977d11…f1699c1` |
| **Verdict** | **`ROT_ARCHITECTURE_REJECTED_R0`** |
| Blocking findings | 2 (1 HIGH, 1 MEDIUM) |
| Correction delta | `11-CORRECTION-DELTA.md` — bounded, two items, no redesign |

## 0. Headline

This is a **near-miss rejection, not a failed architecture**. SRR-1 is a
substantially stronger and smaller candidate than the CP-1/RoT-1 lineage it
replaces. It closes the V-H3 class cleanly, it states the bootstrap impossibility
boundary honestly instead of trying to derive trust, and it survives eleven of the
fourteen mandatory attacks outright. It is rejected on **two bounded defects in the
architecture record**, both of which are enumerated R0 items in the owner's own
frozen boundary, and both of which are correctable in a handful of sentences
without touching the trust chain, the metadata model or the transaction invariant.

Neither blocker requires an R1/R2/R3 control to be pulled forward. No finding in
this report is a stronger-assurance proposal promoted into a requirement.

## 1. Verdict against the exact acceptance rule

The frozen boundary requires all six of the following for
`ROT_ARCHITECTURE_ACCEPTED_R0`:

| # | Acceptance clause | Met? | Basis |
|---|---|---|---|
| 1 | every R0 item is explicit, internally consistent and testable at later gates | **NO** | item 5/8 not internally consistent (SRR-R0-H1); item 12 not explicit as to time, making item 10 untestable (SRR-R0-M1) |
| 2 | no unresolved CRITICAL/HIGH defect that falsifies an R0 normative guarantee | **NO** | SRR-R0-H1 falsifies the stated security objective "rollback below known signed floors is refused" |
| 3 | no unresolved MEDIUM requiring architecture change to meet an R0 guarantee | **NO** | SRR-R0-M1 requires an architecture-record change (a declared time assumption + conditional honesty claim) |
| 4 | every carried R1/R2/R3 concern labelled with its correct lifecycle | yes | `20-LATER-LIFECYCLE-CONDITIONS.md`, nine items, each lifecycle-labelled |
| 5 | no private key, production ceremony or implementation required as evidence | yes | no probe required a key, ceremony, build or binary — see `evidence/PROBES.md` |
| 6 | the verdict identifies the exact reviewed Git commit and document hashes | yes | §0 table above and `evidence/REVIEWED-CONTENT-DIGESTS.txt` |

Clauses 1, 2 and 3 fail. The verdict is therefore `ROT_ARCHITECTURE_REJECTED_R0`.

## 2. Independence and scope

I am a fresh, isolated reviewer. I authored no part of D-0009, ARCH-0003, the
`signed-release-root-v1` pack, OWNER-DIRECTIVE-0004, any RoT-1 revision, any prior
review or the forensic meta-review.

**Read:** the eight authoritative inputs; the owner-supplied Capability Acceptance
Contract v3 (hash-verified, read from file only); the three original governing
documents; D-0007; the AGENT_RUNS schema and `AR-0023.run.yaml`; the r7 review
directory **for house format only**; and — as evidence for attack construction
only — D-0008, ARCH-0002 and the forensic meta-review sections 06 and 11, plus the
r7 consolidated findings. I read parts of `cli/src`, `runtime/src` and Contract v3
Gates A/F/S/T/U to enumerate the product's real privileged ingress surface
(probe PR-6) and to test for pre-existing trust modes (probe PR-4).

**Did not read:** any session or agent transcript, any task-output store, any user
auto-memory file. No finding, verdict or held-out content was written to user
auto-memory.

**Delegation:** none. I spawned no helper session. All work in this report is my own.

**Scope deviations:** none. I implemented nothing, authored no replacement
architecture, created no RoT-1 Revision 8, did not resume CP-1, did not activate or
mutate D-0008/ARCH-0002 (verified unchanged — probe PR-7), did not supersede or
amend D-0007, did not contact the product owner, and wrote only inside
`release/root-of-trust/signed-release-root-v1-review-r0/` plus the mandated
`AR-0023.report.yaml`.

**STOP conditions:** none. All three mandated hashes verified exactly (probe PR-1).
The candidate-identity claim verified exactly (probe PR-2). No required input was
missing. No normative-source conflict required precedence adjudication beyond the
ordinary hierarchy in the frozen boundary §"Normative hierarchy".

## 3. Per-item disposition of the R0 items

The frozen boundary enumerates **fourteen** R0 items; the role instruction
enumerates **twelve**. The fourteen are the contract and govern; the twelve map
onto them without remainder. Disposition is against the fourteen.

| R0 item (frozen boundary) | Disposition | Where established / why not |
|---|---|---|
| 1. pre-existing platform/admin bootstrap assumption | **SATISFIED** | ARCH-0003 §5 names the assumption and explicitly refuses to derive it from "the candidate source, its manifest, its lock, its Git repository or mutually consistent files delivered with it". This is the exact statement the impossibility boundary demands. Best-executed item in the candidate. |
| 2. signed root, delegation and release/targets metadata | **SATISFIED** | ARCH-0003 §3–§4; 00-ARCH "Metadata roles" table, including the negative column (snapshot/timestamp "cannot authorise target bytes"), which is what makes a snapshot/timestamp key compromise non-fatal. |
| 3. binding of release identity, exact payloads and migrations | **SATISFIED** | ARCH-0003 §4 / 00-ARCH:67 bind product identity, version, monotonic sequence, platform/architecture, exact kernel/CLI/payload digests, **schema and migration identities**, minimum secure release, metadata version/expiry. Release *channel* is not bound — non-blocking, SRR-R0-L2 (channel is not an enumerated R0 binding). |
| 4. key delegation, rotation and revocation semantics | **SATISFIED (thin)** | Rotation/revocation authority, threshold (2-of-3 offline root), purpose-restricted snapshot/timestamp roles and monotonic version floors are all stated. Client-side *root succession* semantics are imported by reference from "a mature TUF-style metadata model" rather than restated. The frozen boundary does not enumerate succession chaining, and it explicitly defers library/algorithm selection, so this is an R1 condition (SRR-R0-L1), not a blocker. |
| 5. one verification policy across init, adopt, update, reinstall, rollback, recovery | **NOT SATISFIED** | ARCH-0003 §3.6 claims one policy for all six. The 00-ARCH ingress table then gives `recovery` a second admissible object — "installed valid recovery path" — outside the signed-metadata policy, and omits the floor term that every other backward-capable row carries. **SRR-R0-H1.** |
| 6. verified-byte/use binding | **SATISFIED** | 00-ARCH "Transaction invariant" steps 1–4 and ARCH-0003 §6: verify the exact staged representation, retain a typed authenticated-release handle, install only those measured bytes, never receive a raw source directory. |
| 7. private staging, atomic commit, crash-safe outcome | **SATISFIED** | Transaction invariant steps 5–8: atomic commit of one complete version, verification of the committed representation, durable journal/high-water, and interruption recovery to "the old complete version or new complete version, never a trusted mixed state". Ordering of step 7 relative to 5–6 is an R1 crash-window detail (SRR-R0-L5). |
| 8. signed rollback floors and protected local high-water | **NOT SATISFIED** | The floors themselves are well specified (signed minimum secure release + protected monotonic local high-water, and the pairing correctly serves both stateful and ephemeral/stateless clients). Their *scope* excludes the one ingress that can move a machine backwards without consulting metadata. **SRR-R0-H1.** |
| 9. local authority/Human Gate and headless-policy boundaries | **SATISFIED** | ARCH-0003 §8 and 00-ARCH "Headless CI and multiple machines". The authority for trust-changing automation is administrator/workload policy provisioned **outside** the governed repository and scoped to the exact operation — an owner selection the meta-review had left open. A wording tension with D-0007 T2 is recorded non-blocking as SRR-R0-L3. |
| 10. explicit stale, expired and offline states without false revocation knowledge | **NOT SATISFIED (testability)** | The *semantics* are exactly right and honest: stale/unknown currency, no claim of unseen revocations, monotonic retention of a received revocation/minimum, and no bricking of an authenticated install. But "expired" and "stale" are evaluated against a time source the candidate never names, so the headline honesty claim cannot be stated as a testable condition. **SRR-R0-M1.** |
| 11. separation of authenticity, installed integrity, build provenance, certification, project policy, plugin/retrieval trust | **SATISFIED** | 00-ARCH "Trust-domain boundaries" — an eight-row table with an explicit-limit column per domain. ARCH-0003 §10: "Build provenance and certification evidence inform release eligibility but do not replace release signatures as the client distribution root." This is the strongest part of the candidate and it directly refutes the "make provenance the root" attack. |
| 12. local OS/admin/time/network assumptions and explicit non-guarantees | **NOT SATISFIED** | OS, admin and bootstrap are declared; network is declared through the offline/stale semantics and the "no knowledge of unseen revocations" non-guarantee. **Time is absent entirely** across all seven inputs (probe PR-3). **SRR-R0-M1.** |
| 13. preservation of the original mission and Contract v3 capabilities | **SATISFIED** | 00-ARCH "Preservation of Governance OS" and ARCH-0003 §9/§13 enumerate the preserved capabilities; D-0009 and OWNER-DIRECTIVE-0004 forbid redesigning unrelated capabilities. Contract v3 A2 bullet 8 is the one A2 property the candidate is silent on, but no trust mode exists to masquerade (probe PR-4), so nothing is falsified — SRR-R0-L4, R1. |
| 14. D-0007 active; non-circular first-install authenticity outside its manifest/lock | **SATISFIED** | ARCH-0003 §11, 03-TRANSITION-MAP "D-0007 transition rule", 00-ARCH bootstrap row. D-0007's trust direction is preserved verbatim in effect: ARCH-0003 §6/§8/§9 restate that project records, CLI/environment claims, model and plugin output are requests, never authority. |

Ten of fourteen satisfied outright, one satisfied thinly, three not satisfied —
and the three are produced by only two underlying defects.

## 4. Mandatory attacks — disposition

`REFUTED` = the attack does not succeed against the architecture as written.
`CONFIRMED` = the attack succeeds, or the architecture cannot answer it as written.

| # | Attack | Result | Basis |
|---|---|---|---|
| A-01 | source/repository regenerates its own trusted identity | **REFUTED** | ARCH-0003 §5 excludes the candidate source, manifest, lock, Git repository and "mutually consistent files delivered with it". 00-ARCH bootstrap row: "not derived from candidate files". This is the V-H3 class and it is closed at the architecture level. |
| A-02 | project files / flags / env establish root or approval | **REFUTED** | ARCH-0003 §6 ("Project records and CLI/environment claims are inputs or requests, never authority"), §8 ("Environment variables, repository files and caller/model/plugin claims cannot manufacture trust or approval"), §9 ("It cannot establish or weaken the distribution root"). Also closes the `--dev-root`/`GOV_*` escape-hatch class pre-emptively. |
| A-03 | wrong key | **REFUTED** | Root metadata defines trusted public keys, thresholds and roles; 2-of-3 offline root; delegated release/targets threshold. |
| A-04 | wrong product / wrong platform | **REFUTED** | product/repository identity and supported platform/architecture are bound fields (00-ARCH:67). |
| A-05 | wrong channel | **CONFIRMED (minor)** | "release channel" is used as a scoping concept for CI automation (00-ARCH:123) but is not among the bound metadata fields. Not an enumerated R0 binding → non-blocking, SRR-R0-L2, R1. |
| A-06 | rollback / replay | **CONFIRMED (partial)** | Refuted for the metadata and update paths: monotonic sequence, signed minimum secure release, protected local high-water, "a client never accepts an older metadata version than its protected high-water". **Succeeds through the `recovery` ingress** — SRR-R0-H1. |
| A-07 | metadata expiry / stale-state claims | **CONFIRMED (basis)** | The stale/expired/offline *semantics* are honest and correct. The freeze/replay defence and the honesty claim both rest on an undeclared time source — SRR-R0-M1. |
| A-08 | missing privileged ingress coverage | **REFUTED** | Probe PR-6 enumerated the real command surface (`init`, `adopt`, `update`, `migrate`, `recover`, `release`, `tools`, `plugins`, `skills`, `verify`, `doctor`) against the ingress table. `migrate` consumes already-verified installed bytes with metadata-bound migration identities; `release` is publisher-side; `verify`/`doctor` are read-only; `tools`/`plugins`/`skills` are a deliberately separate trust domain under frozen-boundary R0 item 11 and Contract v3 F2/F3/F4 (recorded as SRR-R0-L6, `NEW_OWNER_DECISION_REQUIRED`). No lifecycle ingress escapes the verifier. |
| A-09 | verify/use TOCTOU, including interruption and recovery | **REFUTED** | Transaction invariant 1–8 closes the classic window on both sides of the commit: verification is of the exact staged representation, installation is from that representation, and the committed representation is re-verified. Crash semantics are specified as an outcome ("old complete version or new complete version"), with mechanism correctly deferred to R1. |
| A-10 | root/release-key rotation and revocation without a universal Trust State | **REFUTED** | Signed metadata versions/expiry plus monotonic floors replace CP-1's universal mutable Trust State and are sufficient. Client-side root succession is imported by reference rather than restated — SRR-R0-L1, R1, non-blocking. |
| A-11 | migration identity confusion | **REFUTED** | Migration identities are bound in release/targets metadata; the `adopt` ingress requires "selected release plus migration identity" as its authenticated object. |
| A-12 | build provenance or retrieval output becomes the release-authentication root | **REFUTED** | ARCH-0003 §10 and the trust-domain table state the negative explicitly in both directions. Retrieval/plugin output is T6-equivalent and cannot self-authorise. |
| A-13 | CI or caller-controlled inputs manufacture trust or Human Gate approval | **REFUTED** | Authority for trust-changing automation is administrator/workload policy provisioned outside the repository; "an environment variable, job input or repository file cannot manufacture one". The wording "Repository gate records remain requests" must be scoped to trust-changing operations at R1 so it does not collide with D-0007 T2 or Contract v3 L2/G2 — SRR-R0-L3, non-blocking. |
| A-14 | local high-water monotonic and separate from repository state | **REFUTED** | "Protected local state", "a persistent machine maintains its own protected metadata/release high-water" — explicitly local, explicitly not a repository record. The pairing of a *signed* minimum secure release with a *local* high-water is what lets ephemeral CI runners (which have no high-water) still resist downgrade; this is a real improvement over the CP-1 stateless-currency defect. |
| A-15 | stale/offline claims honest and compatible with continued ordinary operation | **REFUTED (semantics)** | "Expiry alone does not stop an already authenticated installed system from ordinary governance work" resolves the availability-versus-freshness trade-off the impossibility boundary flagged. Undermined only by the missing time basis — SRR-R0-M1. |
| A-16 | support assumptions and non-guarantees explicit enough to make the claim testable | **CONFIRMED** | OS/admin/bootstrap/network yes; time no — SRR-R0-M1. |

Thirteen refuted (two with non-blocking riders), three confirmed, arising from the
two blocking findings plus one minor R1 condition.

## 5. Findings summary

### Blocking (R0) — see `10-BLOCKING-FINDINGS.md`

| id | sev | title | provenance class | owner action |
|---|---|---|---|---|
| `SRR-R0-H1` | HIGH | Signed rollback floors are scoped only to `rollback`; the `recovery` ingress admits a floor-free, non-metadata-authenticated restore | `NECESSARY-DERIVED` | yes — one bounded trade-off |
| `SRR-R0-M1` | MEDIUM | No time/clock assumption or non-guarantee is declared, although the whole expiry/freshness/stale-honesty model is evaluated against it | `OWNER-ADDED-NORMATIVE` | no |

### Non-blocking — see `20-LATER-LIFECYCLE-CONDITIONS.md`

| id | lifecycle | title |
|---|---|---|
| `SRR-R0-L1` | R1 | Root succession/rotation acceptance semantics imported by reference |
| `SRR-R0-L2` | R1 | Release channel scoping is used but not bound in metadata |
| `SRR-R0-L3` | R1 | "Repository gate records remain requests" must be scoped to trust-changing operations |
| `SRR-R0-L4` | R1 | Contract v3 A2 bullet 8 (trust modes vs certified production) unaddressed — vacuous today |
| `SRR-R0-L5` | R1 | High-water/journal durability ordering relative to atomic commit |
| `SRR-R0-L6` | R1/R2 | Plugin/tool/skill first-acquisition source authenticity — `NEW_OWNER_DECISION_REQUIRED` |
| `SRR-R0-L7` | R1 | Offline/air-gapped install from a held authentic envelope is not designed |
| `SRR-R0-L8` | INFO | R0 traceability table maps 11 of the 14 frozen R0 items |
| `SRR-R0-L9` | R2 | Release/targets threshold value and custody unspecified (correctly deferred) |

## 6. What this review deliberately did not require

Per the frozen boundary §"Not required at R0" and the role instruction, I did not
require and did not fault the candidate for: production signatures or custody
ceremonies; final library, algorithm or expiry-duration selection; any runtime
code; DDC or diverse-compiler proof; supplier-class independence; a reproducible-
builder quorum; two-source first-contact ceremony; proof of organisational
independence; public/cloud/multi-tenant or hostile-admin assurance; G6 or Gate W
completion evidence; or final platform certification.

I also did not treat any historical RoT-1 or CP-1 finding as automatically
binding here. Where a historical attack was still valid in shape (bootstrap
impossibility, ingress coverage, TOCTOU, verified-byte install, rollback and
revocation, stateless currency), I re-derived it against this candidate on its own
terms; where CP-1 mechanisms were retired by OWNER-DIRECTIVE-0004 (universal Trust
State, C0–C3 calculus, bespoke admitter, selector register), I did not reintroduce
them and neither blocking finding depends on any of them.

## 7. Recommended next action

Route `11-CORRECTION-DELTA.md` to the architecture owner as a bounded R0 revision
of ARCH-0003 and `00-ARCHITECTURE.md`. It is two text-level corrections — a floor
scope and an assumption declaration — plus one genuine owner trade-off inside
SRR-R0-H1 (whether a machine whose only complete local state is below its signed
floor may be recovered, and under what authority). No implementation, no new
lineage, no RoT-1 Revision 8, and no change to the trust chain, the metadata model
or the transaction invariant is needed or authorised by this rejection.
