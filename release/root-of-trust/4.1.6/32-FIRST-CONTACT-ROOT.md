# Output 32 — The first-contact root of trust, stated and enforced at its true authority (BC5-1)

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> New in revision 6. It closes blocking class **BC5-1** (review r5 RV5-H1: the first TCB on a machine is selected by the
> independent channels alone) under rule FD-1 (`29`). It separates what code can enforce once an evaluator runs from what
> only the operator procedure can enforce before one runs. It states the remainder exactly as the **first-contact root**, with
> minima computed by the derivation calculator and equal to the executed results. Which sources form that root is owner
> option **OP-13** (`21`; review r5 options T1-a…T1-d). Amended to match: `31` §4, §8, §9; `25` AP-1…AP-3; `06` §2–§3; `01`
> TA-5; `05` §3. Normative keywords: MUST, MUST NOT, SHOULD.

## 1. The class

**Mistaken equivalence (revision 5):** *the typed fingerprint is a good selector of state, therefore of everything it commits
to.* A value typed from one channel page also selected:

| Selector | Revision-5 rule | What one channel page (rank 2, no key) selected |
|---|---|---|
| **lineage** | `25` AP-2 "bootstrap from the typed fingerprint's epoch"; the reference executor took the first self-verifying root v1 in bundle order | a lineage whose every key the attacker generated (RV5-B-A01 A01a/b) |
| **required number of agreeing channels** | `25` AP-3 compared the typed values with `bootstrap.channel_quorum` of the Trust Policy the typed value selects | quorum 1, from the attacker's own Trust Policy (A01c) |
| **evaluator** | `31` R-ADM-2 compared the admitter digest with "the channels", with no quorum; the executor never read `admitter_digests` | a substituted `gov-admit` that admits anything (RV5-D-A02) |

The declared first-admission minima (`30` §10 FA rows, `25` §7, `05` §3, `21` OP-9/OP-12/OP-13) named reproducer, trust-state
and registration keys that the channel attacker did not need.

## 2. Invariant

On a machine with no prior trust, every first-admission selector satisfies one of two conditions. It is an authenticated
value that the values it governs cannot select. Or it is the set of first-contact sources the owner's OP-13 answer names,
stated exactly as the **first-contact root** with its computed minimum. The selectors are the lineage, the state, the number
of agreeing sources and the evaluator.

The required number of agreeing sources is enforced for every first-contact value: lineage, state and admitter digest. It is
enforced by the operator procedure before any evaluator runs, and by the evaluator itself afterwards. Neither enforcement
reads the number from a statement those values select.

## 3. First-contact manifest and first-contact code

One published value commits to every first-contact value, so one agreement rule covers all of them.

**First-contact manifest (FCM)**, `governance-os.first-contact-manifest/1`, canonical JSON (GOV-JCS-1), published by the owner
for every new Trust State and distributed over any carrier (`schemas/first-contact-manifest.schema.json`):

| Field | Content |
|---|---|
| `lineage_id` | the trust-root id (digest of root v1) |
| `state_epoch` | `{root_version, root_digest, policy_version, policy_digest, state_sequence, state_digest}` |
| `admitters` | `{target → SHA-256 of the registered, quorum-reproduced gov-admit for that target}`; equals the selected Trust Policy's `bootstrap.admitter_digests` |
| `issued_at`, `valid_until` (optional) | shown to the operator; past `valid_until` the admitter refuses (`FIRST_CONTACT_MANIFEST_EXPIRED`) |

**First-contact code (FCC):** `gov-fc:<8 hex of lineage id>:<state_sequence>:<64 hex SHA-256 of the canonical FCM>`. The owner
publishes the code in the independent channels (`06` §2). The code replaces the state fingerprint as the value typed at first
contact. The state fingerprint remains the in-gate and `confirm-state` value on admitted binaries (`24` §3.1).

## 4. The operator procedure (FC-1…FC-3): platform tools only, before any evaluator runs

The procedure is TA-5 as restated in `01`. It uses only the platform hash tool (TA-1b: `sha256sum`, `shasum -a 256`,
`certutil -hashfile`) and, under OP-13 (c), the platform's signature verification. `gov trust fc-procedure` prints these steps
for the owner's OP-13 answer. It is documentation, not an evaluator.

| ID | Step | Stop code |
|---|---|---|
| **FC-1** | Read the first-contact code from **each** source the OP-13 answer names (k sources). Continue only if every code read is identical. Fewer than k codes read: stop. | `FIRST_CONTACT_DISAGREEMENT` / `FIRST_CONTACT_SOURCES_BELOW_PROCEDURE` |
| **FC-2** | Fetch the FCM from any carrier; its SHA-256 must equal the code's hash part. | `FIRST_CONTACT_MANIFEST_MISMATCH` |
| **FC-3** | Fetch `gov-admit` from any carrier; its SHA-256 must equal `admitters[target]` of that FCM. Under OP-13 (c) "all agree", its platform code signature must also verify. Under (c) "either suffices", the platform-signed package may replace FC-1 and FC-2: its admitter carries the compiled lineage and the owner's FCM of its build (§7). | `ADMITTER_DIGEST_MISMATCH` / `PLATFORM_SIGNATURE_INVALID` |

**What no code can enforce.** A substituted evaluator ignores FC-4…FC-8. The only defence against evaluator substitution is
that FC-1…FC-3 select the evaluator through the code agreed across the OP-13 sources. The evaluator's selector is therefore
the first-contact root itself (FD-1 §2 (5)). It has rank 2 local authority (a human reading independent sources now) and
current currency. An operator who reads one source and types its value for every required source (A10, atom `op1src`) defeats
FC-1. That shortfall is inside the stated root (§6).

## 5. Admitter rules (FC-4…FC-8): enforced by the genuine evaluator, never read from what the values select

| ID | Rule | Refusal |
|---|---|---|
| **FC-4** | **Compiled first-contact quorum.** The owner's OP-13 answer (number of sources k, agreement rule) is registered source compiled into the admitter. `gov-admit` requires at least k identical typed codes. The selected Trust Policy's `bootstrap.channel_quorum` may only raise that number. | `CHANNEL_QUORUM_NOT_MET` / `CHANNEL_DISAGREEMENT` |
| **FC-5** | **Manifest bound by the code.** The FCM supplied MUST hash to the typed code. It is the only selector of lineage, state epoch and admitter set. | `FIRST_CONTACT_MANIFEST_MISMATCH` / `FIRST_CONTACT_MANIFEST_MALFORMED` / `FIRST_CONTACT_MANIFEST_EXPIRED` |
| **FC-6** | **Lineage from the typed value.** Root v1 is the root whose digest equals the FCM's `lineage_id`. The order of statements in a bundle never changes the result (CR5-B-06). | `ROOT_CHAIN_INVALID` |
| **FC-7** | **Compiled lineage under OP-13 (c) and (d).** An admitter build distributed through the second path or on provisioning media carries the lineage id; an FCM naming another lineage refuses. | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` |
| **FC-8** | **Evaluator binding** (defence in depth, not a substitute for FC-1…FC-4). The admitter's own digest MUST be listed in the selected Trust Policy's `bootstrap.admitter_digests` and not revoked in the selected Trust State. The FCM's admitter set MUST equal that list. | `ADMITTER_NOT_LISTED` / `ADMITTER_REVOKED` / `FIRST_CONTACT_MANIFEST_INCONSISTENT` |

These rules apply to every first admission: first install, CI image build, a legacy consumer's first RoT-1 binary (`11` Phase
4), and a store without an admission record (`31` R-ADM-8′). Re-admission on a machine whose store holds an admission record
also runs FC-1…FC-8. It keeps the store (`31` R-ADM-8′).

## 6. The first-contact root (computed)

The **first-contact root** of an OP-13 answer is the family of minimal first-contact capability sets with which an attacker
holding **no key** makes a machine with no prior trust admit a malicious first TCB. The calculator
(`evidence/r6/CS6-derivation-calculator.py`) models three strategies as substitutions, for every victim class and goal:
- the lineage (`fc_lineage_sub`, rules `V_FC_COMPILED_QUORUM`, `V_FC_LINEAGE`);
- the evaluator (`fc_eval_sub`, rule `V_FC_EVALUATOR`);
- the state within the genuine lineage (`fc_state_root`, which needs the trust-state key).

Atoms: `ch1` and `ch2` are the owner's first-contact sources. `op1src` is the operator typing one source's value for every
required source (TA-5/A10). `alt` is the OP-13 (c) second authentication path. `media` is the OP-13 (d) provisioning media
custody.

<!-- CS6:BEGIN FC-ROOT -->
| OP-13 answer | First-contact root: minimal sets that admit a malicious first TCB with no key | Other minimal sets (release-process compromises, as for running machines) |
|---|---|---|
| a | {ch1} | 1 |
| b | {ch1, ch2}; {ch1, op1src} | 1 |
| c_all_1 | {ch1, alt} | 16 |
| c_all_2 | {ch1, ch2, alt}; {ch1, op1src, alt} | 31 |
| c_either_1 | {ch1}; {alt} | 1 |
| c_either_2 | {alt}; {ch1, ch2}; {ch1, op1src} | 1 |
| d | {media} | 1 |
<!-- CS6:END FC-ROOT -->

Key-theft sets that also need first-contact capabilities (malicious bytes of a genuine registration): sets that contain a root
set above are not minimal, so only the options whose root needs `alt` or `media` show them:

<!-- CS6:BEGIN FC-KEY-THEFT -->
| OP-13 answer | Key-theft minimal sets for malicious bytes of a genuine registration (OP-2 (a), OP-8 = 1, OP-9 (a)) |
|---|---|
| a | none |
| b | none |
| c_all_1 | {2 reproducer keys, transport, ts, ch1}; {2 registration keys, 2 reproducer keys, ts, ch1} |
| c_all_2 | {2 reproducer keys, transport, ts, ch1, ch2}; {2 reproducer keys, transport, ts, ch1, op1src}; {2 registration keys, 2 reproducer keys, ts, ch1, ch2}; {2 registration keys, 2 reproducer keys, ts, ch1, op1src} |
| c_either_1 | none |
| c_either_2 | none |
| d | none |
<!-- CS6:END FC-KEY-THEFT -->

**Executed equality.** For every OP-13 answer, FA6 attacks every subset of the first-contact capabilities with each strategy:
attacker lineage with the genuine admitter, substituted evaluator, attacker-compiled admitter. It runs the procedure and the
reference executor. The minimal accepting subsets equal the calculator's root sets for all seven answers
(`evidence/r6/FA6-first-admission.json` S3).

## 7. OP-13 — the first-contact root (owner option; review r5 T1-a…T1-d)

| Answer | Review r5 | Sources and agreement rule | Trust added | Operational consequence |
|---|---|---|---|---|
| **(a)** | T1-a | one owner source (k = 1) | TA-5 for that source | highest availability; the root is that source alone |
| **(b)** | T1-b | two owner sources under distinct custody (k = 2), compiled quorum over the code (every first-contact value) | TA-5 for both; the operator reads both | first install unavailable while either source is unreachable; custody of two channels; one compromised source gives `FIRST_CONTACT_DISAGREEMENT` or `CHANNEL_QUORUM_NOT_MET` |
| **(c)** | T1-c | a second authentication path independent of the owner's sources: `gov-admit` packages signed by a platform or distribution code-signing service, with compiled lineage and the build's FCM; parameters: agreement rule **all agree** (path and k sources) or **either suffices**, and k ∈ {1, 2} | the signing service's infrastructure joins the first-contact TCB | dependence on the third party's availability and policy; per-platform packaging and signing; "either suffices" adds a root set, "all agree" adds an availability dependency |
| **(d)** | T1-d | physical provisioning media or a hardware token carrying code, FCM and admitter, for designated machines | custody of the media | a ceremony per machine or batch; CI runners only through images built with the media; machines not designated need an (a)–(c) answer |

**What the architecture cannot support** (no computed consequence is offered, and the combination is refused by
`gov trust draft-policy`):
- **OP-13 (c) with OP-12 (b) or (c).** No platform code-signing path authenticates an interpreted admitter script, or a
  helper-machine hand-over, independently of the owner's sources.
- **OP-13 (d) as the only answer** for machines that are not provisioned by media.

**Currency under (c) "either suffices", platform path only.** The state selected is the epoch of the FCM compiled into the
admitter package. That state is the published state as of the package's build: a revocation published later is not seen
until the admitted binary anchors (`24` §3.2). The bound is the FCM's `valid_until`. `gov-admit` shows the epoch's `issued_at`
and age (R-ADM-10).

## 8. Machine classes

| Machine | First-contact sources used | Remark |
|---|---|---|
| First install (M1) | the OP-13 answer | `31` §7 |
| CI runner image | codes and FCM provisioned by the image operator from the OP-13 sources, or the media under (d) | the image build runs FC-1…FC-8; TA-9 |
| Legacy consumer, first RoT-1 binary | the OP-13 answer | `11` Phase 4 |
| Re-admission (`ADMISSION_RECORD_EXPIRED`, OP-15 (a) incident) | the OP-13 answer | store kept (`31` R-ADM-8′) |

## 9. Custody record (CR5-B-02)

The root ceremony record names, for each first-contact source, its custodian and hosting. Under (c) it names the signing
service; under (d) the media custodian. `gov trust draft-policy` flags two sources under one custodian or host
(`FIRST_CONTACT_SOURCES_SHARE_CUSTODY`). Test: RT-180.

## 10. Residuals

| ID | Residual | Bound | Test |
|---|---|---|---|
| **FC-R1** | The first-contact root of the owner's OP-13 answer admits a malicious first TCB with no key | the root sets of §6 exactly; label: `gov-admit` names the sources used and the code's `issued_at` | FA6 S3 (executed equals computed); RT-159 |
| FC-R2 (TA-5/A10) | An operator who types one source's value for every required source | inside FC-R1 (`op1src`); the procedure prints each source's name and requires its page | RT-156 |
| FC-R3 | Under (c): the signing service's compromise, alone ("either") or with the sources ("all") | inside FC-R1 (`alt`) | RT-156 |
| FC-R4 | Under (d): media custody | inside FC-R1 (`media`) | RT-156 |
| RS-B1 (restated) | A stale page selects the state its code names | `issued_at`, `valid_until`, age shown; under (b) and (c) "all" every required source must be stale; the admitted binary anchors next (`24` §3.2) | FA5 `CH1` (FA6 S1) |

## 11. Evidence (`evidence/r6/FA6-first-admission.{py,json}`; executed with real Ed25519 via OpenSSL and `sha256sum`)

| OP-13 | One page shows an attacker lineage | All pages show it | Operator types one value | Substituted evaluator, one page | Substituted evaluator, all pages | Second path compromised alone |
|---|---|---|---|---|---|---|
| (a) | `ACCEPTED` (root) | `ACCEPTED` (root) | `ACCEPTED` (root) | admitted (root) | admitted (root) | — |
| (b) | `FIRST_CONTACT_DISAGREEMENT` | `ACCEPTED` (root) | `CHANNEL_QUORUM_NOT_MET`; typed twice (A10): `ACCEPTED` (root) | `FIRST_CONTACT_DISAGREEMENT` | admitted (root) | — |
| (c) all, k = 1 | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | `PLATFORM_SIGNATURE_INVALID` | `PLATFORM_SIGNATURE_INVALID` | `ADMITTER_DIGEST_MISMATCH` |
| (c) all, k = 2 | `FIRST_CONTACT_DISAGREEMENT` | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | `CHANNEL_QUORUM_NOT_MET` | `PLATFORM_SIGNATURE_INVALID` | `PLATFORM_SIGNATURE_INVALID` | `ADMITTER_DIGEST_MISMATCH` |
| (c) either, k = 1 | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | admitted (root) | admitted (root) | admitted (root) |
| (c) either, k = 2 | `FIRST_CONTACT_DISAGREEMENT` | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | `CHANNEL_QUORUM_NOT_MET` | `FIRST_CONTACT_DISAGREEMENT` | admitted (root) | admitted (root) |
| (d) | sources compromised, media intact: `RELEASE_UNREGISTERED` | | | | | media custody compromised: admitted (root) |

"Root" marks a result inside the stated root of §6. Honest sources are `ACCEPTED` under every answer.

Further rows:
- Evaluator binding and procedure: `ADMITTER_NOT_LISTED`, `ADMITTER_REVOKED`, `FIRST_CONTACT_MANIFEST_INCONSISTENT`,
  `FIRST_CONTACT_MANIFEST_MISMATCH` (a manifest other than the one the code names), and FC-1/FC-2/FC-3 stop codes.
- Bundle order (ORD-1…ORD-3): attacker root served first, genuine code `ACCEPTED`.
- Single-rule mutants: `quorum_from_selected_state`, `lineage_from_bundle_order`, `skip_compiled_lineage`,
  `skip_evaluator_binding`, `skip_fcm_consistency` and `skip_fcm_digest_check` are each detected (S7).
- The revision-5 FA5 harness on the revision-6 executor: 45/45 scenarios, 17/17 vectors, 26/27 mutants, unchanged (S1).
