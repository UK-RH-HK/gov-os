# P2-AR-0013: iteration-0 capability baseline re-audit, family `alpha`

| Field | Value |
|---|---|
| Run | P2-AR-0013 (fresh, independent `capability-family-auditor`; model `claude-opus-5[1m]`, Opus 5, 1M context) |
| Handoffs | P2-HO-0009 (re-audit common), P2-HO-0000 (common protocol), P2-HO-0001 (alpha scope) |
| Candidate | `cap2-candidate-0` = `57177a37ea296ece16b185874831462b6a76db18`; worktree HEAD `3b8a4ab4…` (candidate + one orchestration-only commit) |
| `product_code_digest` | `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547` (verified; identical to `srr1-r1-accepted`) |
| Scope | Gates A (A1–A5), B (B1–B3), S (S1–S6), T (T1–T3): 17 capabilities, 100 checklist bullets |
| Verdict | `FAMILY_AUDIT_COMPLETE` |
| Machine-readable | `capability-audit.yaml`, `findings.yaml`; probes and outputs under `evidence/` |

## 1. Result in one table

| Cap | Title | Status | Bullets P / partial | Qualification impact | Findings (**blocking**) |
|---|---|---|---|---|---|
| A1 | Canonical authority and policy precedence | PARTIAL | 5 / 1 | CANNOT_UNDERMINE | A0-A1-01, **A0-A1-02** |
| A2 | Authentic root of trust | PARTIAL | 5 / 5 | **COULD_UNDERMINE** | **A0-A2-01**, **A0-A2-02**, **A0-A2-03**, **A0-A2-04**, A0-S5-02, A0-A2-05, **A0-B3-01**, **A0-A1-02** |
| A3 | Security, sensitivity and permissions | PARTIAL | 5 / 1 | **COULD_UNDERMINE** | **A0-A2-04**, **A0-T2-01**, A0-A3-01, A0-A3-02, **A0-A1-02** |
| A4 | Budget/resource governance | PARTIAL | 0 / 4 | CANNOT_UNDERMINE | A0-A4-01, **A0-A1-02** |
| A5 | Emergency controls | PARTIAL | 3 / 3 | CANNOT_UNDERMINE | A0-A5-01, A0-A5-02, A0-A5-03, **A0-A1-02** |
| B1 | Standard repository contract | PRESENT_AND_SUBSTANTIAL | 4 / 0 | — | A0-B1-01 (INFO), **A0-A1-02**, **A0-B3-01** |
| B2 | Path map | PARTIAL | 3 / 2 | CANNOT_UNDERMINE | A0-B2-01, A0-B2-02, **A0-B3-01**, **A0-A1-02** |
| B3 | Authoritative vs derived state | PRESENT_AND_SUBSTANTIAL | 4 / 0 | — | **A0-B3-01**, **A0-A1-02** |
| S1 | Canonical OS repo | PRESENT_AND_SUBSTANTIAL | 2 / 0 | — | **A0-A1-02** |
| S2 | Immutable releases | PARTIAL | 10 / 1 | CANNOT_UNDERMINE | A0-S2-01, **A0-A2-04**, **A0-A1-02** |
| S3 | `gov init` | PARTIAL | 5 / 1 | CANNOT_UNDERMINE | A0-S3-01, **A0-A2-02**, A0-S4-03, **A0-A1-02** |
| S4 | `gov adopt` (A0–A11) | PARTIAL | 6 / 6 | **COULD_UNDERMINE** | A0-S4-01, A0-S4-02, A0-S4-03, **A0-T2-01**, **A0-B3-01**, **A0-A1-02** |
| S5 | `gov update` | PARTIAL | 5 / 4 | **COULD_UNDERMINE** | **A0-A2-04**, **A0-A2-02**, A0-S5-01, A0-S5-02, **A0-A1-02** |
| S6 | Cross-machine mechanics | PARTIAL | 2 / 1 | CANNOT_UNDERMINE | **A0-A2-03**, **A0-B3-01**, **A0-A1-02** |
| T1 | Role separation | PARTIAL | 2 / 7 | **COULD_UNDERMINE** | **A0-T2-01**, A0-S4-03, **A0-A1-02** |
| T2 | Fresh-session independence | PARTIAL | 0 / 2 | **COULD_UNDERMINE** | **A0-T2-01**, **A0-B3-01**, **A0-A1-02** |
| T3 | Adoption evidence tree | PARTIAL | 0 / 1 | **COULD_UNDERMINE** | **A0-T2-01**, **A0-B3-01**, **A0-A1-02** |

Totals: **PRESENT_AND_SUBSTANTIAL 3, PARTIAL 14, ABSENT 0, UNCLEAR 0, N/A_WITH_REASON 0**. Bullets: 61
PRESENT_AND_SUBSTANTIAL, 39 PARTIAL. No capability was N/A. The reference retrieval profile in S3 bullet 6 does not
exist before Phase 5, but the bullet was evaluated on the bootstrap mechanism, which does exist. Findings: 25 (4 HIGH,
13 MEDIUM, 4 LOW, 4 INFO). **7 are blocking.**

**AC-4 (A2) determination: NOT MET.** The R1 acceptance is still valid for this candidate: the product digest is
unchanged, and I reproduced the R1 behaviour classes myself (§4). A2 as Contract v3 specifies it is not fully
incorporated. Bullets 146 (consistent post-install rewrite, A0-A2-01), 149 (lock identity, A0-A2-03) and 150
(certification masquerade, A0-A2-04) are falsified on every machine. Bullets 143/147 hold only on a provisioned
machine, and the product's default posture is unprovisioned (A0-A2-02, owner decision).

## 2. Method

- **Pinned inputs** (`evidence/00-pinned-inputs.out`). HEAD `3b8a4ab4…`. `product_identity.py` gives the same
  `product_code_digest` `bd4d65d9…0547` for HEAD, `cap2-candidate-0` and `srr1-r1-accepted`. HEAD differs from the
  candidate only by the P2-HO-0009 handoff file. Contract v3 SHA-256 is `4c2df291…5ed3`, byte-identical to its canonical
  import. The frozen gate contract SHA-256 is `d2f33e89…a25e` and matches `ORCHESTRATOR_STATE.yaml`. No mismatch, no STOP.
- **Build and regression** (`evidence/00-build-and-regression.*`). `~/.cargo/bin/cargo build --release` (binary
  sha256 `3271ce0e…be81d`); `cargo test --release --lib` 42/42; `cargo test --release --test certification` 79/79,
  with HOME redirected to scratch and XDG unset. These builder tests are regression evidence only (O3). A variant
  run with `XDG_CACHE_HOME` pointing at a path without a `.cache` segment fails
  `repair2::framework_lock_is_release_identifying_and_portable` (78/79,
  `evidence/00-regression-variant-xdg-cache.*`). That run is evidence for A0-A2-03. AC-15's default-environment
  regression is green.
- **Capability and bullet universe** came from the owner source, not from the derived views: Contract v3 lines
  130–203 and 894–973, with 100 bullets and challenge lines 140, 154, 164 and 197. The derived views were then checked
  against it (`evidence/C0-contract-derived-views.*`, finding A0-A1-02).
- **Independent evidence.** Every bullet has its own probe output. The 24 probes, plus the pinned-input and regression scripts, drive `target/release/gov` against
  disposable projects in scratch sandboxes. Each sandbox has its own HOME/XDG_*, GOV_* is stripped, and git
  config is isolated, so neither the operator's machine state nor the product tree is touched. Signed-release
  scenarios use an **independent Python ed25519 minter** (`evidence/lib/srr_mint.py`) that reimplements the envelope,
  keyid, root/release/snapshot/timestamp/break-glass documents and payload measurement from ARCH-0003. Its measurement
  agrees with the product's: every authentic case is admitted AUTHENTIC, and A2-02 [P1] shows installed payload ==
  signed payload. Throw-away administrator roots are provisioned from an admin directory
  outside every project. Each probe's docstring gives its exact command. Each output line carries a `[TAG]` that the
  YAML records cite.
- **What was not read**, per P2-HO-0009: the earlier alpha evidence (`audit-0/alpha/`), `P2-AR-0001.*`, any
  other family's evidence, session or agent transcripts, task-output stores, and user memory.

## 3. Pinned-input and environment notes

- A default workstation keeps its embedded-kernel cache in `~/.cache`, and all probes use that default unless a probe
  varies it deliberately (A2-04 [L4], S6 [X3]).
- `gov trust provision` refuses an anchor under the current working directory, so the harness provisions from `$HOME`
  (A2-02 [P0]).
- The brownfield fixture ships `memory/chat_history.sql`; its README says a harness builds the sqlite store from it.
  The end-to-end S4 run does that (`S4-adopt-end-to-end.out` [SETUP]). The raw dump was also run
  (`S4-adopt-raw-sql-chat-store.out`, finding A0-S4-02).
- The host has no `pytest`, so A0's recorded baseline test status is "failed" (`/usr/bin/python3: No module named
  pytest`). That is an environment fact, not a product defect.

## 4. A2 and AC-4: mapping to the Phase-1 R1 evidence and re-establishment on this candidate

R1 was accepted by AR-0033 (`release/verification/4.1.6-r1-4/00-VERIFICATION-REPORT.md` §8, item-by-item disposition of the frozen R1 section) on
`srr1-r1-candidate-4`, which is byte-identical to this candidate. AC-14 therefore does not require the R1 held-out suites to be re-run, and I did not re-run
them. I re-established each R1-class behaviour I rely on with my own minter and probes.

| A2 bullet (line) | R1 evidence that bears on it | Examined by R1? | Re-established here | Status |
|---|---|---|---|---|
| 143 authenticity before staging/install | R1 items 2, 4, 5; AR-0027 §1 accepted the unprovisioned posture as an IMPLEMENTATION-CHOICE | yes, provisioned; unprovisioned accepted on honesty grounds | A2-02 [P1]-[P9] refusals leave nothing installed; A2-01 [U2]-[U4] default posture installs tampered bytes | PARTIAL (A0-A2-02) |
| 144 integrity ≠ authenticity | R1 item 8 (AR-0033 `hv_d::d7`) | yes | A2-01 [U2], A2-03 [T2] | PRESENT |
| 145 shared non-circular root across ingresses | R1 item 4 (five admit/install pairs); AR-0027 break-glass item 9 | yes | A2-02 per-ingress refusals; A2-00 census; A2-06 [O4]; A2-07 | PRESENT |
| 146 post-install tampering detected | R1 item 8 (D-0007 controls effective) | **consistent manifest/lock rewrite not examined**: no R1 report under `release/verification/4.1.6-r1*/` records it (searched) | A2-03 [T1] detected; [T2] consistent rewrite accepted | PARTIAL (A0-A2-01) |
| 147 pre-install tampering detected | R1 item 3 | yes | A2-02 [P2]-[P5d], [P8], [P9]; A2-06 [O2] | PARTIAL (A0-A2-02) |
| 148 source cannot regenerate its own identity | R1 item 2 | yes | A2-02 [P6], [P0]; A2-01 [U4] (UNKNOWN, no trust created) | PRESENT |
| 149 lock records, does not invent | none directly (item 5 covers bytes, not lock fields) | **not examined** | A2-04 [L1] [L3] [L4]; S6 [X3] | PARTIAL (A0-A2-03) |
| 150 no masquerade as certified production | R1 item 9 (env/CLI/project inputs cannot create trust); `4.1.6-r1-3/00-VERIFICATION-REPORT.md:92` notes `release::build` as the only writer of a certification status (§6 below-floor context) | **unsigned certification claim as an update-gate input not examined** | A2-02 [P9] env refused; A2-04 [L2] unsigned CERTIFIED removes the update gate | PARTIAL (A0-A2-04) |
| 151 rotation/revocation/recovery | builder `srr::root_succession…`, the OWNER-DECISION-0006 requirements 1–10 table in AR-0027's report (`release/verification/4.1.6-r1/00-VERIFICATION-REPORT.md` line 357 onward); the rotation drill is R2 | partly (break-glass); the succession rules were not independently attacked | A2-05 [K1]-[K6c] | PRESENT |
| 152 offline after authentic envelope | AR-0027 break-glass item 10 (break-glass only); SRR-R0-L7 owner-closed first-install offline | **only break-glass offline** | A2-06 [O0]-[O5] in a network namespace with no route | PRESENT |

The Phase-1 residuals seen again on this candidate are listed below. They stay R2 items and are not Phase-2
blockers. AR27-N5: a `minimum_secure_release` published without a sequence never raises the floor (A2-05 [K5b]).
AR27-N7: evidence-map rows are all `NOT_YET_MAPPED`. The frozen Phase-2 contract makes that half of A0-A1-02 a P2
criterion (AC-10/AC-13).

## 5. Cross-capability interaction S3/S4/S5 ↔ A2 (AC-16), exercised

Every lifecycle ingress goes through the one verifier. The call-site census is `evidence/A2-00-ingress-census.out`:
five `srr::admit` sites, each followed by one of the only five `install_kernel` calls; `Ingress::Recovery` is never
constructed; `gov recover` writes no kernel bytes. On a provisioned machine the same attack set was run through each
ingress with the same typed refusals and nothing installed:

| Ingress | Unsigned | Tampered after signing | Below floor | Authentic |
|---|---|---|---|---|
| `gov init` (S3) | SRR_RELEASE_UNVERIFIED [P6] | SRR_PAYLOAD_DIGEST_MISMATCH [P2] | SRR_BELOW_FLOOR [P7] | AUTHENTIC [P1] |
| `gov adopt migrate` batch 0 (S4) | SRR_RELEASE_UNVERIFIED [P8] | SRR_PAYLOAD_DIGEST_MISMATCH [P8] | SRR_BELOW_FLOOR [P8] | AUTHENTIC [P8] |
| `gov update --apply` (S5) | SRR_RELEASE_UNVERIFIED [P9] | SRR_PAYLOAD_DIGEST_MISMATCH [P9] | (floor via rollback/reinstall) | AUTHENTIC [P9] |
| `gov kernel reinstall` | PREVIOUSLY_VERIFIED_BY_THIS_MACHINE when bytes match the record [P9] | SRR_PAYLOAD_DIGEST_MISMATCH [P9] | SRR_BELOW_FLOOR / SRR_BREAK_GLASS_NOT_AUTHORISED [P9] | AUTHENTIC [P9] |
| `gov update --rollback` (S5) | — | — | SRR_RELEASE_UNVERIFIED [P9], [K6b] | — (A0-S5-02) |

The same interaction fails on the default unprovisioned machine, where every row admits with authenticity UNKNOWN
(A0-A2-02). The update ingress's gate decision also reads an unsigned field (A0-A2-04).

## 6. S4: the twelve adoption stages, driven end-to-end

`evidence/S4-adopt-end-to-end.out` runs the brownfield fixture, prepared per its README, from A0 to A11 with
separate sessions per protocol role, and forces refusals along the way. The negative paths are in
`evidence/S4-T2-B2-negative.out`, and the as-shipped raw dump run is in `evidence/S4-adopt-raw-sql-chat-store.out`.

| Stage | Result | Status |
|---|---|---|
| order | later stage before A0 → ADOPTION_NOT_STARTED | — |
| A0 | commit pinned, baseline tests recorded; no branch/worktree, no snapshot, dirty path truncated `rc/app/main.py`; interrupted work only advised [N6] | PARTIAL (A0-S4-01) |
| A1 | 35 entries = every tracked file, kinds for provider rules, chat/index stores, secrets, manifests | PRESENT |
| A2 | 35 classified, class+authority+id each; legacy rules LEGACY, superseded decision SUPERSEDED, dead code flagged | PRESENT |
| A3 | 35 map entries with protocol fields; nothing moved | PRESENT |
| A4 | 8 dependency-ordered batches with rollback snapshots; destructive batch gated | PRESENT |
| A5 | A6 before review refused; same-session review refused; verdict binds no digest; any role string accepted | PARTIAL (A0-T2-01, A0-S4-02) |
| A6 | batches with tests and ledger; destructive entries held until gates answered, then executed; batch rollback reverts moves and links [N5]; post-approval edits executed [N2]; `--role` ignored | PARTIAL (A0-T2-01, A0-S4-02, A0-S4-03) |
| A7 | executor session refused; divergence rejected and VERDICT_CONFLICT on a false claim [N3]; accepted with 0 tests after they were emptied [N2] | PARTIAL (A0-T2-01) |
| A8 | jsonl and sqlite stores extracted as PROVISIONAL with provenance, secret string skipped, stores retired to the archive, archived legacy rules kept as temporary evidence | PRESENT |
| A9 | 213 artefacts / 526 chunks / 503 vectors / 16 edges / 16 symbols after A7; secrets excluded | PRESENT |
| A10 | builder session refused; accepted recall@k 0.897 on the builder-generated held-out set | PARTIAL (A0-T2-01) |
| A11 | 15 §18 criteria plus deep audit and doctor; verdict NOT_ADOPTED_HEALTHY for the unremediated fixture (correct); no independence check | PARTIAL (A0-T2-01) |

T3: all 13 protocol §5 files and the migration ledger are present, and stage status and verdicts are recorded with
sessions and roles. The chain is traceable by id but not bound by digest (A0-T2-01).

## 7. Blocking findings

| ID | Cap | Sev | Blocks | Owner decision | Summary |
|---|---|---|---|---|---|
| A0-A2-01 | A2 | HIGH | AC-4, AC-3 | **yes**: D-0007 T1 anchor; anchor for machines without a protected record | A consistent payload + KERNEL_MANIFEST.json + framework.lock rewrite passes kernel verify, guards, doctor and audit, and `never_index_classes: []` becomes effective. The protected installed record is never consulted after install. |
| A0-A2-02 | A2, S3, S5 | HIGH | AC-4, AC-3 | **yes**: embed/pre-install production root keys, refuse unprovisioned installs, or accept the posture (conflicts with the R1 IMPLEMENTATION-CHOICE) | The default unprovisioned machine installs tampered or self-identified releases at every ingress with authenticity UNKNOWN, presented as CURRENT; doctor is silent. |
| A0-A2-03 | A2, S6 | MEDIUM | AC-4 | no | The lock records release_commit from the unsigned manifest (forged value accepted on an AUTHENTIC install), records no authenticity basis, and embedded-install identity varies with XDG_CACHE_HOME. |
| A0-A2-04 | A2, A3, S2, S5 | HIGH | AC-4, AC-3 | no | An unsigned `manifest.json` edited to CERTIFIED removes the update Human Decision Gate on a genuinely signed release; any role can mint CERTIFIED. |
| A0-T2-01 | T2, T1, T3, S4, A3 | HIGH | AC-3 | no | Adoption verdicts bind no reviewed artefact. After approval the executor emptied the tests and turned a KEEP into an ungated DELETE of an imported module, and A6 and A7 accepted. Roles are free strings, independence is session-string inequality, A11 is unchecked, and A10 uses the builder's held-out set. |
| A0-A1-02 | all 17 | MEDIUM | AC-10, AC-13 | no | The compiled contract carries headings only (0 of 100 bullets, none of the per-capability fields); the evidence map gives every alpha capability zero owners. |
| A0-B3-01 | A2, B1, B2, B3, S4, S6, T2, T3 | MEDIUM | AC-10 | no | Green-suite currency (D021) ignores spec beyond decisions, product source, index manifest, adoption evidence, trust state and the gov binary. |

Non-blocking findings are recorded in `findings.yaml`. The substantive ones:
- A0-A1-01: the context-packet constitution comes from the unverified kernel.
- A0-A4-01: network and experiment budgets are not enforced.
- A0-A5-01/02/03: FREEZE_WRITES leaks, CANCEL_AGENTS revokes nothing, and resume is unaudited.
- A0-S3-01: a REJECTED release installs silently.
- A0-S4-01/02/03: A0 baseline gaps, a plan/scaffold contradiction, and `--role` ignored on init/adopt.
- A0-S5-01: a phantom rollback ledger entry.
- A0-S5-02: a refused reinstall leaves a half-installed kernel, and provisioned rollback cannot run.

## 8. Freshness, health-scheduler tiers, qualification coverage

- **Freshness** (`evidence/FRESH-invalidation.out`). Invalidation was demonstrated for 9 input classes. For
  spec/requirements, product source, the index manifest, adoption evidence and machine trust changes, D021 stays
  current (A0-B3-01). Per capability: demonstrated (true) for A1, A3, A4, S2, S3, S5. For A3, source-content evidence
  goes stale through index freshness D010. Not demonstrated (false, because a relevant input leaves green evidence
  current) for A2, B1, B2, B3, S4, S6, T2, T3. Not attempted for A5, S1, T1.
- **Tiers.** No G0–G6 scheduler or tier identifier exists anywhere in `runtime/src`, `cli/src` or `framework/`. What
  runs instead: per-command guards (authority, kernel trust, control state, budget thresholds), which are
  G0-equivalent; on-demand doctor and audit families; and the doctor + audit that init, update and adopt A11 run
  themselves, which are G5-equivalent. `evidence_owner_actually_runs` is therefore `partial` for every capability.
  The tier mapping and AC-5 themselves belong to another family.
- **Qualification coverage.** Every capability has a Repo A and Repo B challenge, a hidden-oracle fault class, and
  chaos/retrieval entries or a "not relevant" reason. Four capabilities also name a route outside synthetic
  repositories: A2 (key custody → R2 ceremony/drill), A4 (real provider spend), S1 (canonical layout → R2
  clean-clone), and T1/T2 (actual session holder / model context → harness attestation).

## 9. What could not be established, and why

- **Key custody, production signatures and the rotation drill** are R2 (frozen SRR boundary). Only the product
  mechanics were exercised, with throw-away keys.
- **G-tier behaviour** could not be exercised because no scheduler exists (see §8).
- **Overlay loss via the phantom rollback of A0-S5-01** follows from the code path but was not separately exercised.
- **`gov update --apply` across a major version with an incomplete migration chain** was checked only at `--check`
  (`S1-S2-release.out` [M4]: `compatible: true` from the release's `supported_from_versions`, with
  `migration_path_complete: false` and a human gate recommended). Apply was not run.
- **Real outbound transport and real provider spend** are outside the product. The upstream remote transport is not
  configured, and spend is self-reported through `gov route --record`.
- **Who actually holds a session.** The acting role and session are caller-declared (the D-0007 documented
  boundary). T1/T2 findings are limited to what the OS could enforce inside that boundary.

## 10. Evidence index (`evidence/`)

| File | Covers |
|---|---|
| `00-pinned-inputs.sh/.out` | identities, hashes, toolchain |
| `00-build-and-regression.sh/.out`, `00-regression-variant-xdg-cache.sh/.out` | build, lib 42/42, certification 79/79; XDG variant 78/79 |
| `lib/env.sh`, `lib/srr_mint.py` | sandbox isolation; independent SRR metadata minter and gov driver |
| `A1-policy-precedence.py/.out` | A1 all bullets; A0-A1-01 |
| `A2-00-ingress-census.sh/.out` | A2.3, AC-16 call-site census |
| `A2-01-unprovisioned-posture.py/.out` | A2.1/5/6/8 on the default posture; A0-A2-02 |
| `A2-02-provisioned-ingress.py/.out` | A2.1/3/5/6/8, AC-16 per ingress |
| `A2-03-post-install-tamper.py/.out` | A2.2/4; A0-A2-01 |
| `A2-04-lock-identity-and-masquerade.py/.out` | A2.7/8, S5.1; A0-A2-03, A0-A2-04 |
| `A2-05-rotation-revocation-recovery.py/.out` | A2.9, break-glass, S5.8; A0-S5-02 |
| `A2-06-offline-verification.py/.out` | A2.10 in a network namespace |
| `A2-07-interrupted-install.py/.out` | interrupted-install challenge; A0-A2-05 |
| `A2-08-reinstall-version-change.py/.out` | reinstall failure atomicity; A0-S5-02 |
| `A3-security-sensitivity.py/.out` | A3 all bullets |
| `A4-budget-governance.py/.out` | A4 all bullets; A0-A4-01 |
| `A5-emergency-controls.py/.out` | A5 all bullets; A0-A5-01/02/03 |
| `B-repository-contract.py/.out` | B1, B3 |
| `C0-contract-derived-views.py/.out` | contract binding; A0-A1-02 |
| `FRESH-invalidation.py/.out` | freshness for all capabilities; A0-B3-01 |
| `S1-S2-release.py/.out` | S1, S2 |
| `S3-init.py/.out`, `S3-S4-role-flag-authority.py/.out` | S3; A0-S3-01, A0-S4-03 |
| `S4-adopt-end-to-end.py/.out`, `S4-adopt-raw-sql-chat-store.out` | S4 A0–A11, T3; A0-S4-01/02 |
| `S4-T2-B2-negative.py/.out` | B2, T2, S4 negative paths; A0-T2-01, A0-B2-01/02 |
| `S5-update.py/.out` | S5; A0-S5-01 |
| `S6-cross-machine.py/.out` | S6 |
| `T1-roles.py/.out` | T1 |
