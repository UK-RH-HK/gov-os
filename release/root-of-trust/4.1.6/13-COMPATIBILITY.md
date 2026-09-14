# Output 13 — Legacy-version compatibility model

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 makes three replacements:
> - the sentinel boundary and LC-1/LC-2 give way to the legacy-path-occupation layout and the executed property LP-1
>   (`26`, R2-H4);
> - historical identities move into the root-signed Trust Policy;
> - F1 is superseded by P3r3 (R2-L3).

## 1. Legacy artefacts in scope

| Artefact | Revision 3 treatment | Section |
|---|---|---|
| Kernels of releases 4.1.2–4.1.5 | listed in TPS `eligibility.historical_releases[]`; never eligible; their surfaces also fail E7 | §2 |
| Pre-RoT binaries (4.1.2–4.1.5) opening RoT-1 projects | legacy-path occupation: fail before any write, executed over their full registers | §3, `26` |
| Future trust formats and layouts | readers refuse unknown formats or layouts | §4 |
| Legacy-layout projects under a RoT-1 binary | `LEGACY` state, read-only, layout migration by update | §5 |
| 4.1.x snapshots and runtime residue | quarantined; historical targets refused | §6 |
| Environment variables and CLI | removals, restrictions, new commands | §7 |
| Prior harnesses and review evidence | expected results | §8 |
| Revision-1 and revision-2 statement formats | never issued; not accepted | §9 |

## 2. Historical kernels (4.1.2–4.1.5)

- **Recognition.** TPS v1 `eligibility.historical_releases[]` lists version, release id, release commit, tree digest
  (`9964830b…`, `6bebfdbb…`, `e5e2f2c7…`, `962f9848…`), manifest digest, `REJECTED` and the verifier report digest. It is
  root-signed as part of the TPS.
- **Withdrawn statement type.** Revision 2's threshold-1 `historical-identity` statement is withdrawn (`05` §2). The set
  is protected at root threshold and named by the Trust Base Manifest (`25` §8).
- **Status.** `HISTORICAL_IDENTIFIED`, `INELIGIBLE(historical)`, always.
- **Independent failure.** Their constitutional surfaces fail the TPS v1 inventory. 4.1.2 has an unclassified
  `approve_cit` plus 64 registration violations; 4.1.3 and 4.1.4 have 64 and 62 violations
  (`evidence/CSI-check-legacy-*.json`).
- **Consumer consequence.** A project on a legacy kernel opened by a RoT-1 binary is read-only until updated to an
  eligible signed release. The update performs the layout migration of `26` §7.

## 3. Pre-RoT binaries

The design, class argument and evidence are in `26`. In summary:

- **Layout.** RoT-1 authority lives under `governance/trust/`; the overlay moves to `governance/overlay/`, views to
  `governance/views/`.
- **Occupation.** `governance/kernel`, `governance/project`, `governance/generated`, `governance/framework.lock`,
  `spec/audits/GOVERNANCE-ADOPTION` and `.governance-runtime/migration` are occupied by entries of the wrong type.
- **LP-1 (executed).** For 4.1.2, 4.1.3, 4.1.4 and 4.1.5, across 695 invocations derived from their own registers
  (104/109/115/119 leaf commands) and 40 stateful chains, with a legacy update snapshot and a restricted classification
  present:
  - no byte outside `.git/` and `.governance-runtime/` changed;
  - Git state is unchanged;
  - the classification survived.

  Controls: 36–47 changing invocations per binary on an ordinary legacy project. Ablation: 4 changing invocations per
  binary without the adoption occupations.
- **Withdrawn.** LC-1 ("availability impact only") and LC-2 ("RoT-1 cannot change their behaviour through data") are
  withdrawn as false (review r2 R2-H4). LC-3 is superseded.
- **Superseded evidence.** The revision-2 F1 probe (`evidence/F1-*`) remains as history. It wrote `FORMAT` as `rot-1\n`
  instead of the specified JSON, omitted lock `kernel.*` fields, and ran one destructive command. It supports no claim in
  revision 3.

## 4. Future format and layout evolution

- `governance/trust/FORMAT` is `{"layout":"legacy-path-occupation-v1","minimum_reader":"4.1.6","trust_format":"rot-1"}`
  in GOV-JCS-1 bytes. It is read first.
- A binary that does not implement the named `trust_format` or `layout`, or whose version is below `minimum_reader`,
  stops with `TRUST_FORMAT_UNSUPPORTED`. It never falls back.
- A future format keeps the occupation principle. It occupies the previous format's authority paths with wrong-typed
  entries, and every older RoT-1 binary fails before writing, by the same argument as `26` §3.
- Format and layout changes are install transactions.

## 5. Legacy-layout projects under a RoT-1 binary

| Consumer state | Installation state (`18` §9) | Allowed | Path forward |
|---|---|---|---|
| lock 1.1.0 file, `governance/kernel/` directory, kernel equals a historical digest | `LEGACY` + `HISTORICAL_IDENTIFIED`, `INELIGIBLE(historical)` | read-only; remedies | anchor the machine (`24`), then `gov update --apply --source <signed eligible release>`: `framework_update` trust gate, layout migration (`26` §7), lock 3.0.0 |
| legacy layout, unknown kernel | `LEGACY` | read-only | same |
| RoT-1 layout, eligible final | `COMPLETE` | per freshness | — |
| RoT-1 layout, unknown format or layout | `FORMAT_UNSUPPORTED` | `gov version`, `gov doctor` | upgrade `gov` |

## 6. Snapshots and runtime residue from 4.1.x

- `.governance-runtime/update/<v>/` holds legacy kernels. The first RoT-1 transaction on the machine quarantines it to
  `.governance-runtime/legacy-quarantine/`. As a restore target it is a historical identity:
  `SNAPSHOT_INELIGIBLE(historical)`.
- Legacy adoption snapshots `.governance-runtime/migration/batch-N/` are quarantined. The path is then occupied by a
  tracked file (`26` §3.1).
- Rolling back from 4.1.6 to 4.1.5 is refused. Recovery from a defective 4.1.6 is a newer eligible release or
  `kernel reinstall` of 4.1.6.

## 7. Environment variables and CLI changes

| Item | Revision 3 |
|---|---|
| `GOV_KERNEL_SOURCE`, `GOV_KERNEL_CACHE` | removed |
| `GOV_CANONICAL_ROOT` | source selection only |
| `HOME`, `XDG_*`, `GOV_*` | never select the VTS, pins or decision pins (account database) |
| `gov kernel reinstall --source <arbitrary>` | must authenticate to the installed statement digest |
| Trust refusals | `ok: false` with typed codes (API-0002 exit 1) |
| `gov update --rollback` to a legacy snapshot | refused |
| New commands | `gov trust show`, `confirm-root`, **`confirm-state`**, **`confirm <gate>`**, `adopt-lineage`, `refresh --from`, `export`, `publish` (producer), **`verify-artifact`** (`25` §5), **`draft-policy`** (drafts the Constitutional Surface Inventory, `23` §6.2); `gov release attach-signature`, `promote`; `gov kernel export`, **`gov kernel show <path>`** (snapshot bytes with CI, `18` §12) |
| `gov decide` on a trust gate | `TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED` (`27`) |
| Paths | overlay `governance/overlay/`, views `governance/views/`, RoT-1 lock `governance/trust/framework.lock`, adoption evidence `spec/audits/ADOPTION/`, transaction area `.governance-runtime/trust-tx/` |

## 8. Prior harnesses and review evidence — expected results

The prior harnesses run with `GOV_CANONICAL_ROOT` pointing at a clone of the 4.1.6 final tag, with a pinned or confirmed
anchor on the verifier machine.

| Harness | `gov` (production profile) | `gov-test-profile` |
|---|---|---|
| `release/verification/4.1.2/heldout/harness.py` | As 4.1.5, except (a) HV-11 (unsigned `prev-4.1.1`): `UNSIGNED_SOURCE_REFUSED`; (b) scenarios reading `governance/kernel/`, `governance/project/` or `governance/framework.lock` paths directly now see occupation entries. Each is classified as an intended layout change and re-proven on the RoT-1 paths. | 36/1/1 with RoT-1 paths |
| `release/verification/4.1.3/heldout-new/harness_v2.py` | historical installs refused `RELEASE_INELIGIBLE(historical)`; classified and re-proven with signed test-profile equivalents | 13/2 |
| `release/verification/4.1.4/heldout-v3/harness_v3.py` | 14/2 (VV-05, VV-07 frozen to 4.1.4); layout and historical classifications as above | 14/2 |
| `release/verification/4.1.5/heldout-wv/harness_wv.py` | 6/0 with classifications as above | 6/0 |
| Review r1 `R1-legacy-kernel-floors.py` (pointed at 4.1.6) | **must flip** | — |
| Review r1 `R2b-use-time-toctou.py` | **must flip** | — |
| Escalation `probe.sh` E1–E5 | every probe refused or not verified | — |
| Review r2 `P1-floor-coverage.py` harm tests (a)–(c) against a release whose unfloored leaves are weakened | **must flip**: E7 ineligible, effective policy genuine (architect evidence `P1r3`) | — |
| Review r2 `P2-gate-record-forgery.py` | **must flip**: the edited repository record is a request; `TRUST_GATE_LOCAL_CONFIRMATION_REQUIRED` | — |
| Review r2 `P3-pre-rot-binary-matrix.py` on a genuine 4.1.6 project | **must hold LP-1** for the real 4.1.2–4.1.5 binaries (architect evidence `P3r3`) | — |
| Review r2 `P4-trust-state-model.py` scenarios | the implementation's trust-state module MUST reproduce `P4r3` (34 of 34) | — |

Any other change is a regression, unless the verifier independently classifies it as an intended refusal and re-proves
the original property.

## 9. Revision-1 and revision-2 statement formats

- **Revision-1 payloadTypes:** never issued, never accepted.
- **Revision-2 drafts:** `artifact-final.v1` under `release-final`, `historical-identity.v1`, `trust-policy.v1` with
  `floors[]`, `trust-state.v1` without `prior_states`. These were never issued.
- **Revision 3 compiles:**
  - `artifact-final.v2` under `release-artifact`;
  - `build-attestation.v1`;
  - `trust-policy.v2` with `surface`;
  - `trust-state.v2` with `prior_states`, `artifacts` and resolved references.
- No revision-3 binary accepts the revision-2 draft payloadTypes.

## 10. Other compatibility consequences

| Area | Change | Mitigation |
|---|---|---|
| Layout | overlay and views renamed; legacy names occupied; adoption evidence renamed | one install transaction; Git renames; documentation and templates updated |
| Mixed teams | legacy binaries cannot operate a RoT-1 project | intended (`26`); the release protocol retires 4.1.2–4.1.5 |
| CI runners | an anchor is needed for governed mutation under OP-7 (a)–(c) | state pins in runner images, or OP-7 (c) witnesses |
| Every final release that changes constitutional content | a TPS registration at root threshold | `gov trust draft-policy`; `14` RK-17 |
| Trust gates | local confirmation per machine | operator decision pins for automation (`27` §3.2) |
| Agents | kernel content through `gov kernel show` and context packets | adapters carry pointers (`18` §12) |
| Dependencies, platforms, performance | as revision 2, plus a same-filesystem transaction area | `TRUST_PLATFORM_UNSUPPORTED(cross_device_tx)` |
