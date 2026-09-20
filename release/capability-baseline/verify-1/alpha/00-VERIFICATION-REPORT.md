# P2-AR-0046 — verification iteration 1, capability family **alpha**

| Field | Value |
|---|---|
| Run | **P2-AR-0046** (fresh, independent family verifier) |
| Family | **alpha** — A1–A5, B1–B3, S1–S6, T1–T3 (17 capabilities, **100 checklist bullets**) |
| Candidate | `cap2-candidate-1` |
| Candidate commit | `0bad524d836f179964ffbac31972856ea6434682` |
| `product_code_digest` | `e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220` |
| `governed_state_digest` | `3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0` |
| Worktree / branch | `…/scratchpad/wt/p2-verify1-alpha`, `phase2/verify-1-alpha` |
| Verdict | **`FAMILY_VERIFICATION_COMPLETE`** |
| Blocking findings | **2** (V1-S4-01 HIGH, V1-S5-01 MEDIUM) — both **RESIDUAL**, no materially-new blocker class |

I authored none of the implementation, none of its tests, none of the iteration-0 audits, none of the
repairs and no Phase-1 role. Every status below rests on evidence I produced on this candidate. No
iteration-0 status was adopted, and nothing in `release/capability-baseline/repair-1/**` is cited as
evidence.

---

## 1. Pinned inputs (verified)

```
git rev-list -n1 cap2-candidate-1        → 0bad524d836f179964ffbac31972856ea6434682   ✓ matches dispatch
git rev-parse HEAD                       → 8588813ec1ef9c832879e258ca5acfb573ae996f   (later orchestration commit)
product_identity.py HEAD                 → product_code_digest   e6332fc7…2220       ✓
                                           governed_state_digest 3d2aeba2…20c0       ✓
product_identity.py cap2-candidate-1     → same two digests                          ✓
sha256 Governance_OS_Capability_Acceptance_Contract_v3.md
                                         → 4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3 ✓
sha256 GATES/PHASE-2-FROZEN-GATE-CONTRACT.md
                                         → d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e ✓
```

No STOP. One INFO note: `product_identity.py cap2-candidate-1` prints the **annotated tag object id**
(`f75eb7db…`) on its `commit:` line rather than the tagged commit; both digests it prints are correct
(finding `V1-AC09-01`, the same tooling issue the synthesis recorded as `S0-AC09-01`).

Sources applied as given: OD-P2-01, OD-P2-02, OD-P2-03, P2-ADJ-0001, P2-ADJ-0002, P2-ADJ-0003. I record
no finding that any of them is wrongly implemented.

## 2. Method

The audit universe is the **owner source** (Contract v3 lines 130–203 and 894–973), parsed directly:
100 bullets across 17 capabilities. Each bullet was established by constructing an input, running the
product and capturing the observable result.

**The signing side is mine.** `heldout/lib/srrsign.py` is an independent Signed-Release-Root metadata
producer I wrote from the on-disk format in `runtime/src/srr/metadata.rs`, `binding.rs` and
`human_channel.rs`, using python-`cryptography`'s ed25519 — a different implementation from the
`ed25519-dalek` the product verifies with, and deliberately **not** the product's own
`tests/certification/srr_material.rs`. Every root, release, snapshot, timestamp, T2 binding authority,
break-glass token and owner-signed human answer in this verification was minted by it, per run, into a
throw-away administrator-domain directory outside every repository.

**Machines** are simulated the way a real installation works: a distinct `XDG_STATE_HOME` and `HOME`
per machine, with `GOV_MACHINE_STATE_DIR` deliberately never set, so every probe takes the product's
own protected-state path. Dev/test machines provision a throw-away root first (OD-P2-02).

Seven held-out suites, re-runnable with `heldout/RUN-ALL`:

| Suite | Scope | Result |
|---|---|---|
| `t01_a2_root_of_trust.py` | A2 bullet by bullet | **54 / 55** |
| `t02_cross_machine.py` | **the cross-machine attack** (S6, P2-ADJ-0002, OD-P2-02, SRR-R0-L4) | **74 / 74** |
| `t03_gate_a.py` | A1, A3, A4, A5 | **53 / 58** |
| `t04_adopt_roles.py` | S4 A0–A11, T1–T3, relocated OS stores on a legacy tree, B2.3 | **67 / 68** |
| `t05_release_init_update.py` | S1, S2, S3, S5 (full update lifecycle) | **59 / 61** |
| `t06_gate_b_contract_freshness.py` | B1–B3, the derived contract views, freshness (AC-10/AC-13) | **80 / 81** |
| `t07_prior_findings.py` | first-hand disposition of the remaining iteration-0 findings | **11 / 15** |

**412 checks, 398 pass.** Every one of the 14 failing checks is a finding of §4 and nothing else:
`t01` the update-ingress instance of V1-S5-01; `t03` V1-A4-01 and the four A5 checks behind
V1-A5-01/-02; `t04` V1-S4-01; `t05` V1-S2-01 and V1-S5-01; `t06` V1-B2-01; `t07` V1-A3-01, the two
A0 checks behind V1-S4-02 and V1-AC09-01.

Regression (O3/AC-15, reproduced by me in this worktree): `cargo test --lib` → **276 passed, 0 failed**.
`cargo test --test certification` was started in the same worktree and had not finished when this
verification closed — the host was running several Phase-2 verifiers at a load average above 160.
That is recorded in `evidence/cargo-certification.NOT-COMPLETED.md`, not omitted. It affects no
capability status here (every status rests on the held-out suites), but it leaves one input of
**AC-15** unestablished by this run. Builder tests are cited as regression evidence only.

## 3. Per-capability result

| Capability | Bullets | Status | Bullets not met |
|---|---|---|---|
| A1 Canonical authority and policy precedence | 6 | `PRESENT_AND_SUBSTANTIAL` | — |
| A2 Authentic root of trust *(POST_VERIFICATION_HARDENING)* | 10 | `PRESENT_AND_SUBSTANTIAL` | — |
| A3 Security, sensitivity and permissions | 6 | `PRESENT_AND_SUBSTANTIAL` | — |
| A4 Budget/resource governance | 4 | `PARTIAL` | :168 network-call budget not enforced |
| A5 Emergency controls | 6 | `PARTIAL` | :173/:174 two rebuild commands mutate tracked state; :178 recovery not durably recorded |
| B1 Standard repository contract | 4 | `PRESENT_AND_SUBSTANTIAL` | — |
| B2 Path map | 5 | `PARTIAL` | :192 SPLIT/MERGE not executable |
| B3 Authoritative vs derived state | 4 | `PRESENT_AND_SUBSTANTIAL` | — |
| S1 Canonical OS repo | 2 | `PRESENT_AND_SUBSTANTIAL` | — |
| S2 Immutable releases | 11 | `PARTIAL` | :907 no capability/plugin versions |
| S3 `gov init` | 6 | `PRESENT_AND_SUBSTANTIAL` | — |
| S4 `gov adopt` | 12 | `PARTIAL` | :929 A6 hard-blocked on a secret-bearing brownfield tree; :923 A0 takes no branch/snapshot |
| S5 `gov update` | 9 | `PARTIAL` | :938 "already up to date" decided from an unauthenticated source |
| S6 Cross-machine mechanics | 3 | `PRESENT_AND_SUBSTANTIAL` | — |
| T1 Role separation | 9 | `PRESENT_AND_SUBSTANTIAL` | — |
| T2 Fresh-session independence | 2 | `PRESENT_AND_SUBSTANTIAL` | — |
| T3 Adoption evidence tree | 1 | `PRESENT_AND_SUBSTANTIAL` | — |

**11 `PRESENT_AND_SUBSTANTIAL`, 6 `PARTIAL`, 0 `ABSENT`, 0 `UNCLEAR`, 0 `N/A_WITH_REASON`.**
**91 of the 100 bullets are `PRESENT_AND_SUBSTANTIAL`; 9 are `PARTIAL`.** No required capability is
`ABSENT` or `UNCLEAR`, so **AC-2 is met by this family**; each `PARTIAL` carries its AC-3 argument in
`capability-audit.yaml`, two of which (S4, S5) I judge `COULD_UNDERMINE` and therefore blocking.

## 4. Findings

Two block; seven do not. **Every finding is RESIDUAL. This iteration introduced no materially-new
blocker class in family alpha.**

| Id | Cap | Sev | Blocking | Label | Title |
|---|---|---|---|---|---|
| **V1-S4-01** | S4 | HIGH | **yes** (AC-3) | RESIDUAL / **BC-P2-33** | A6 is hard-blocked on a brownfield tree whose secret-bearing files A2 already classified SECRET |
| **V1-S5-01** | S5, A2 | MEDIUM | **yes** (AC-3) | RESIDUAL / **BC-P2-37** | `gov update` reports "already up to date" from the candidate's unauthenticated declared version |
| V1-A5-01 | A5 | MEDIUM | no | RESIDUAL / BC-P2-08 | `rebuild-memory` / `memory rebuild` change tracked state under FREEZE_WRITES and PAUSE |
| V1-A4-01 | A4 | MEDIUM | no | RESIDUAL / — (A0-A4-01) | the network-call budget is observed but not enforced |
| V1-A5-02 | A5 | LOW | no | RESIDUAL / — (A0-A5-03) | recovery from an emergency control leaves no durable reasoned record |
| V1-A5-03 | A5 | LOW | no | RESIDUAL / — (A0-A5-02) | CANCEL_AGENTS revokes no claim or handoff |
| V1-B2-01 | B2 | LOW | no | RESIDUAL / — (A0-B2-01) | SPLIT and MERGE are not executable |
| V1-S2-01 | S2 | LOW | no | RESIDUAL / — (A0-S2-01) | no capability/plugin versions in the release manifest |
| V1-S4-02 | S4 | LOW | no | RESIDUAL / — (A0-S4-01) | A0 creates no adoption branch/worktree and takes no snapshot |
| V1-A3-01 | A3 | LOW | no | RESIDUAL / — (A0-A3-01) | unclassified personal data is indexed (owner posture question) |
| V1-AC09-01 | tooling | INFO | no | RESIDUAL / — (S0-AC09-01) | `product_identity.py <tag>` prints the tag object id as `commit` |

### 4.1 V1-S4-01 (blocking)

`gov adopt classify` (A2) classifies `src/app/config.py` and `memory/chat_history.sql` of the product's
own brownfield fixture as class **SECRET**, sensitivity `secret`, confidence 0.99. Nothing writes that
classification into the project's `DATA_SENSITIVITY.yaml`, so the health checks `D011` and
`path_map_compliance` (both **critical, scope global**) stay active and hard-block `adopt.migrate`.
Their `remedies` list names `cit.*`, `task.*`, `handoff.create` and `update.apply` — **no adoption
stage**. A6–A11 are therefore unreachable through the documented A0–A11 sequence: the operator must
hand-edit the sensitivity overlay to classify the files the OS itself already classified. With that
one out-of-band edit applied, every batch and every remaining stage runs, which is how I was able to
grade A6–A11 at all.

Why blocking: it leaves **AC-3** unmet for S4. Contract v3's own advanced-qualification challenge for
A3 (:164) seeds secrets and B2's Repo-B challenge (:197) is a tree of exactly this shape, so a
qualification run of the adoption path on Repo B stalls at A6 instead of measuring A6–A11.

### 4.2 V1-S5-01 (blocking)

`update::check` reads the candidate's identity from the **unauthenticated** `KERNEL.yaml` /
`KERNEL_MANIFEST.json` of the source directory, and `apply_update_opts` returns
`{"applied": false, "reason": "already up to date"}` with `ok: true` whenever that declared version is
not newer — **before the single verification policy runs**. On a provisioned machine I observed this
for a payload-tampered source, a source signed by a different owner's root and a correctly signed
source below the machine's floor. Nothing is installed in any case and `framework.lock` is unchanged;
the defect is the affirmative report on a source whose authenticity was never established.

Why blocking: it leaves **AC-3** unmet for S5's "authenticated source" bullet. A Phase-4 fault class of
the shape "the update source has been tampered with" is answered `ok: true` whenever the tampered
source keeps the installed version string, so the oracle would record no refusal where one is due.

I record this as the one judgement in this report that a synthesis verifier may reasonably weigh
differently: the exposure is narrow (it needs the declared version to equal the installed one) and
admits nothing.

### 4.3 The non-blocking `PARTIAL`s, argued (AC-3)

* **A4** — the classes that can run away without a human (model/API spend, daily spend, parallel
  agents, tool-install cost) are enforced and each stops at a Human Decision Gate; the network-call
  overrun is reported in `telemetry summary.over_budget`, and Phase-4 runs offline.
* **A5** — the two escaping commands regenerate derived index manifests deterministically from
  authoritative truth and create or alter no governed fact; every record-writing and lifecycle command
  is refused. Recovery is observable in telemetry although it is not durably recorded.
* **B2** — the vocabulary expresses SPLIT and MERGE, the refusal is typed and names its route (a manual
  CIT), and nothing mis-executes.
* **S2** — every capability the release ships is inside the payload the signed metadata binds by
  per-file digest, so what ships is pinned even though the capability version vocabulary is not
  itemised.

## 5. The cross-machine attack (this family's lead duty)

Five simulated machines, each with its own protected state root and `HOME`:

| | posture |
|---|---|
| **A** | provisioned from the owner's root **and** bound to the owner's T2 binding authority |
| **B** | provisioned **and** bound — the owner's second machine |
| **C** | provisioned from the owner's root, **not** bound ("a machine the provisioning did not authorise") |
| **D** | unprovisioned |
| **E** | provisioned from a **different owner's** root and bound to that owner's authority |

**74 of 74 checks pass.** Machine A installed an authentic release and wrote four kinds of OS state —
a Human Decision Gate record, two audit records, a task and a CIT. All six sealed records carry the
portable scope (`hmac-sha256/t2-v2`) under the owner's authority.

* **Continuity.** After a `git clone`, machine B honours every fact A wrote: `gov gate show` reports
  `t2.binding = VERIFIED` with the authority and key id, `gov audit` raises no open T2 finding, and
  `gov status` reconstructs the project. A gate B writes verifies back on A — the round trip holds.
* **Refusals, each typed.** C, D and E all report the same record as `FOREIGN` with a stated reason;
  a hand-edited record is `BROKEN` naming the sealing operation and time; a record with its seal
  stripped is `UNSEALED`; a seal under a key the current authority no longer lists is `UNAUTHORISED`.
  Restoring the record makes it `VERIFIED` again. A record the foreign owner's machine wrote in its own
  project is `FOREIGN` when transplanted into A's tree. The broken record makes the governance suite
  fail and names the record.
* **Authority attacks.** `T2_BINDING_UNPROVISIONED` (unprovisioned machine), `SRR_THRESHOLD_NOT_MET`
  (authority signed by a root-delegated key that is not the `t2-binding` role, and by a key the root
  does not know), `T2_BINDING_AUTHORITY_EXPIRED`, `T2_BINDING_AUTHORITY_ROLLBACK` (an older version
  after a rotation), `T2_BINDING_KEY_NOT_AUTHORISED`, `T2_BINDING_MACHINE_NOT_AUTHORISED`. A rotation
  is accepted and seals under the revoked key stop being honoured immediately.
* **Nothing secret in any repository.** A byte search of the whole project tree for the binding key and
  for each of the seven role private keys finds nothing.
* **`gov` verifies and never signs** (SRR-R0-L4). The trust surface exposes no signing subcommand, and
  the release binary contains no `SigningKey` / `from_private_bytes` / `secret_key` symbol.
* **The second machine's path.** A clone is `KERNEL_UNANCHORED` until that machine verifies the release
  the project pins (ARCH-0003 §8). The refusal is typed, names `gov kernel reinstall --source …` as its
  remedy, and leaves `status`, `doctor`, `kernel trust` and `kernel verify` available — the availability
  rule holds. After anchoring, `rebuild-memory` and governed writes work.
* **OD-P2-02.** An unprovisioned machine refuses external-source kernel ingress; the embedded payload
  installs only as a marked `BOOTSTRAP_EMBEDDED_PAYLOAD` with authenticity `UNKNOWN`, never presented as
  current, and disclosed by `status`, `doctor` and `audit`.
* **S6 b3.** The two machines' `framework.lock` agree on `release_hash`, `version` and
  `kernel_manifest_hash`, and no lock value is an absolute path.

## 6. The other iteration-1 duties

* **A2 per bullet** — all ten bullets established on this candidate with metadata I signed
  (§ `capability-audit.yaml` A2). BC-P2-35, BC-P2-36 and the A2 half of BC-P2-37 are closed.
* **`gov adopt` A0–A11 on a brownfield tree** — driven end to end. Twelve stages, independence enforced
  at A5/A7/A10/A11, an approval bound to digests of the plan, catalogue and tests (a semantic change to
  any of the three refuses execution with `APPROVAL_STALE`), A10 refusing the builder's own held-out
  set, and A11 returning `ADOPTED_HEALTHY` on a tree whose A10 accepted. A6's block is V1-S4-01.
* **`gov update` including health admission and rollback** — a complete lifecycle: check/impact, the
  Human Decision Gate answered through the **owner-signed human channel** (an answer I signed with the
  root-delegated `human-gate` key, dropped into the machine's protected inbox; `--approve` and `--by`
  are explicitly not substitutes), the commit (authenticity AUTHENTIC, migration applied, overlay
  preserved byte for byte, indexes rebuilt, doctor+audit run, ledger written), a default-refused
  below-floor rollback, and a rollback admitted by an owner-signed recovery token that marks the machine
  `DEGRADED — RECOVERY ONLY`. Health admission refuses an update that remedies none of the active
  blocks, naming the blocks and the subjects.
* **Relocated OS stores through adopt/update/migrate on a legacy tree** — `claims.db` and `control.json`
  live in `.governance-state/`; a control file left at the legacy runtime path is still honoured
  (strictest state wins) and is relocated on the next control command; adoption runs afterwards;
  removing `.governance-runtime/` entirely leaves project truth and the OS stores intact.

## 7. Cross-capability interactions (AC-16, this family's row)

**S3/S4/S5 ↔ A2** — every lifecycle ingress passes through the one verifier: `init` and
`kernel reinstall` refuse a tampered source with `SRR_PAYLOAD_DIGEST_MISMATCH`; `update --apply`
refuses an unsigned and a foreign-signed target and installs only the owner-signed one, recording its
authenticity in the lock and the ledger; `update --rollback` is refused `SRR_BELOW_FLOOR` and admitted
only by an owner-signed token; `adopt` runs on a kernel this machine anchored. The one seam is
V1-S5-01, where the update ingress reports on a source it has not authenticated.

## 8. Freshness (AC-10 for this family)

From a legitimately green baseline (`gov audit` green=true, verdict HEALTHY — P2-ADJ-0003: the probe
builds a baseline that is green under the contract, not a vacuous one), changing **an authoritative
spec decision**, **product source**, **the project policy overlay** and **the index manifest** each
makes the next governed operation stop treating the green record as current. Every alpha capability has
at least one evidence owner in the evidence map, with named automated checks and tiers.

## 9. What I could not establish

1. **`cargo test --test certification`** had not finished when this verification closed; the host was
   running several verifiers at load >160. `cargo test --lib` reproduced 276 passed / 0 failed. See
   `evidence/cargo-certification.NOT-COMPLETED.md`; a completed run must be read before AC-15 is
   called met.
2. **Two BC-P2-03 input classes** — a change to the **machine trust anchor** and a change to the **`gov`
   binary** — were not exercised as freshness triggers. I established four of the six input classes the
   iteration-0 finding named.
3. **CANCEL_AGENTS claim revocation** was not exercised end to end: the probe could not establish a
   claimed task on its fixture, so `V1-A5-03` rests on the absence of any consumer of `agents_cancelled`
   outside `control::state`, not on a demonstrated failure.
4. **A11 on the brownfield tree** was reached only through its gating behaviour (`STAGE_ORDER` while A10
   had not accepted). A11's own audit was exercised on a greenfield-adopted tree where A10 accepted.
   A11 against a brownfield tree's full legacy surface is untested here.
5. **R2 material** — production key custody, a key ceremony, rotation/revocation drills, SBOM/licence
   provenance and private-remote publication are out of this gate and were not assessed. The keys used
   here are throw-away, drawn per run.
6. **AC-14 (R1 preservation)** is P2-AR-0044's; I re-established the R1-relevant A2 behaviour for the
   areas this family exercises but did not re-run the R1 held-out suites.

## 10. Outputs

```
release/capability-baseline/verify-1/alpha/
  00-VERIFICATION-REPORT.md          this file
  capability-audit.yaml              17 capabilities, 100 bullets, per-bullet status and evidence
  findings.yaml                      11 findings, each labelled RESIDUAL with its reason
  prior-findings-disposition.yaml    every iteration-0 finding in scope: CLOSED / RESIDUAL
  heldout/                           7 suites + lib/ (the independent signer and harness) + RUN-ALL
  evidence/                          captured output of every suite and of the pinned-input checks
```

`heldout/RUN-ALL` re-runs everything and prints one PASS/FAIL line per check. The checks that fail on
this candidate **are** the findings above; RUN-ALL exits non-zero while any of them fails, so a later
candidate that closes them exits 0.
