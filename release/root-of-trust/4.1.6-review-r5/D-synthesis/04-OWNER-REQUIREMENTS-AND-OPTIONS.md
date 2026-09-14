# D-synthesis 04 — Owner requirements (HO-0001 §3–§4) and owner options (review r5)

Each requirement is judged as a class: `SATISFIED` or `NOT SATISFIED`. Sub-items name their decisive evidence; "reproduced"
refers to `01-REPRODUCTION.md`.

## 1. HO-0001 §3 requirements

### 1.1 §3.1 Constitutional-floor closure — **NOT SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| Complete constitutional key inventory | holds | CSI check `framework/` exit 0; self-test 71/71 (reproduced) |
| Default-deny handling of unknown constitutional keys | holds, with RV4-L1 open (wildcard `informational` rule) | self-test S01–S03; D-A05 N1 exit 2; RV5-B-A11 exit 2 (reproduced); review r4 B part U U01, U02 exit 0 |
| Explicit floor mode for each mutable field | holds | inventory; lint |
| Coverage check fails the release | holds | checker exits 0/3/2/2/2 on framework/4.1.5/4.1.2/4.1.3/4.1.4 (reproduced) |
| Schema evolution cannot silently introduce an unfloored setting | holds for classification; **fails** for the value of classified non-orderable units, which a lower-authority selector chooses | D-A05 N1/N2; RV5-H3 (D-A01, D-A05 N3) |

| HO-0001 §3.1 test list | Determination | Evidence |
|---|---|---|
| Role → authority map | holds | self-test S04–S06; P1r4 on real 4.1.5 (reproduced) |
| **Sensitivity and indexing exclusions** | **fails** | D-A01: {pipeline, `release-candidate`, `release-final`} makes a weakened secret pattern effective; on 4.1.5 the `ASIA…` key file is indexed and served. RV5-B-A09: a non-identical weakening reported by nothing (RV5-M2). |
| Irreversible Human Gate authority | holds | floor leaves; self-test S09, S27; P1r4 ceiling |
| **Plugin and tool permission floor** | **fails for tool descriptors** (pinned members, including commands `gov` executes) | RV5-B-A09 tool command: E7 exit 0, no reduction; D-A01's route applies to every non-join unit |
| Outbound and export controls | holds | floor leaves; self-test S11 |
| Project override controls | holds | P1r4 (reproduced); self-test S26–S30, S45, S53–S55 |
| Install and update authority | holds | self-test S15 |
| Exception authority | holds | self-test S16, S55 |
| A future unknown constitutional field | holds for classification | self-test S01–S03; D-A05 N1 |

### 1.2 §3.2 New-machine trust bootstrap — **NOT SATISFIED**

| Machine or rule | Determination | Evidence |
|---|---|---|
| **First install** | **fails** | RV5-H1: what first admission requires is misstated (channels alone, zero keys); OP-13 (b) is read from the selected state; one channel selects the evaluator. RV5-M8: a user-writable installation is C0 only under OP-7 (a)/(b). |
| Clean CI runner | holds, with carried RV5-L2, RV5-L5 | RV5-B-A12 M2 rows (reproduced); image record expiry |
| Restored from backup | holds, with carried RV5-L3 and RV5-M3 | A12 M3 rows; re-admission discards the store |
| Old trust epoch | holds | A12 M4 rows; P4r5 retained `M4_old_epoch` |
| No trust epoch | holds | A12 M5 rows |
| Two machines at different epochs | holds | A12 M6 rows |
| Offline machine after a long absence | holds, with RV5-L3 | A12 M7 rows |
| Safety distinguished from freshness | holds | `24` §2; 296 rows, 0 `current` |
| What each machine may do, what is gated, what needs a witness, what is persisted, OP-7's effect | holds except the user-writable installation class (RV5-M8) and re-admission (RV5-M3) | D-A03; A12 M8 |
| Transport or repository attacker cannot select old signed state as a current fact | holds | A12: C3 never on a thief descendant; C3 on states below t9 only in stated residual rows (RS-B1, RS-1b, TA-7) |
| Signed-state replay | holds | P4r5 retained `R1_signed_state_replay` (reproduced) |
| Gate records from repository state | holds | P4r5 retained `R3_gate_record_from_repository` (reproduced) |

### 1.3 §3.3 Binary and root authenticity — **NOT SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| Options evaluated (threshold root signature, separate attestation, certification binding, reproducible build, compiled digests, multi-signature) | holds as an evaluation | `25` §2 |
| A single lower-threshold release key cannot mint a malicious binary | holds | CS5 self-checks and INV-ONE (reproduced); P4r5 VA5 rows |
| **The binary** | **fails** | RV5-H2: the build environment selects the bytes of every reproducer. RV5-H1: at first contact, one channel selects the evaluator and the lineage. |
| Compiled trust roots, minimum floors, trust-policy identity, historical-release set, trust state and bootstrap rules | **inherit RV5-H2** | they are files of the registered source, compiled by the same common-mode environment |
| **Non-circular trust chain** | holds in running mode (P4r5 reproduced); **fails at first contact** (RV5-H1) | — |
| Executors of the one predicate agree | carried | RV5-M9 (D-A04) |

### 1.4 §3.4 Legacy-binary damage containment — **SATISFIED**

| Sub-item | Determination | Evidence |
|---|---|---|
| Kernel, legacy lock, trust, rollback, reinstall, init-force and migration paths | holds | reviewer C `matrix5` re-run: 30,165 rows; property R2-H4 0 violations; LP-1r 1,335 rows, 0 project writes; 0 classifications lost; 0 Git-operation trees written into `COMPLETE`. Reviewer C's reproduction of the review r4 C matrix, P3r3 and ST5 re-run (`01` §4). |
| Defence does not depend on old binaries understanding RoT-1 | holds | occupation by entry type; closed trust entry sets |
| No silent mutation of kernel or trust state into a state treated as valid | holds | as above; carried RV5-M6, RV5-M7, RV5-L7, RV5-L8 |

### 1.5 §4 Forward-compatibility constraint — **SATISFIED for classification**

| Sub-item | Determination | Evidence |
|---|---|---|
| New constitutional files and keys classified without another architecture revision | holds | D-A05 N1 (default deny, exit 2), N2 (classified `pinned_file`, exit 0); self-test S02, S22; owner-domain binding groups S66/S67 |
| Content of a new kernel-shipped file fixed at the right authority | **inherits RV5-H3** | D-A05 N3: an attacker's contract YAML exit 0 under the CI-derived registration; N5 no reduction |
| Hash-bound normative source plus compiled executable | note RV5-I2 | binding groups bind digests, not the derivation |

## 2. Owner options OP-1 … OP-15

### 2.1 Pre-decided?

**No.**
- D-0008 has no `chosen_option`; every `owner_parameters_pending` entry says "(no proposal)"; `21` states no proposal.
- `recommended_option: C` is the decision record's architecture option, not an owner parameter.
- **Inconsistency (text, not a decision):** `24` §9 keeps revision 4's labelled OP-7 proposal, and `24` §5 lists "assumed
  parameters ... proposals only" (RV5-L4).

### 2.2 Honest about security consequences?

**No.**

| Option | Determination | Finding |
|---|---|---|
| OP-1 | incomplete: no minimum root threshold stated | RV5-L6 |
| OP-2 | (a) and (b): false for constitutional content. {pipeline, `release-candidate`, `release-final`} registers malicious content under either answer. (b) additionally: {two delegated custodians, `release-final`} with no OP-8 verification. | RV5-H3 |
| OP-3 | mode B consequence incomplete: each certified update still needs a currency proof naming the publishing TSS | RV5-L9 |
| OP-4 | false: "neither `release-candidate` nor `release-final` selects ... a policy root; they appear in no minimal set" | RV5-H3 |
| OP-5 | accurate | — |
| OP-6 | accurate as stated; the lineage confirmed is whatever the consulted channel shows | RV5-H1 |
| OP-7 | incomplete for user-writable installations: C0 only under (a), (b), and (c) without witnesses. Clock text caveats. | RV5-M8; RV5-L3, L4 |
| OP-8 | false by omission: no effect on content; verification records are reused by source and inputs | RV5-H3 |
| OP-9 | false for first admission (channels alone); key-theft sets overstated by `transport` | RV5-H1; RV5-M1 |
| OP-10 | incomplete: the build environment is common-mode and not covered | RV5-H2 |
| OP-11 | accurate ((a) states RR-2); the combination with re-admission is unstated | RV5-M3 |
| OP-12 | incomplete: every form is selected by one channel's digest, with no binding to `admitter_digests` or negatives | RV5-H1 |
| OP-13 | false: (a) the channel alone suffices with zero keys; (b) the quorum is read from the selected state and does not cover the admitter digest | RV5-H1 |
| OP-14 | (b) incomplete: re-admission discards monotonic state; the workstation installation burden is unstated | RV5-M3; RV5-M8 |
| OP-15 | (a) incomplete: the incident path through `gov-admit` discards monotonic state | RV5-M3 |

### 2.3 Complete?

**No.**
- **First-contact root.** No option sizes it beyond "one or two owner channels": no second authentication path, no physical
  provisioning, and the admitter digest is outside OP-13. This is a genuine owner trade-off (`11` CD5-1).
- **Build environment.** No option covers the common-mode build environment; OP-10 covers the toolchain archive only. This
  is a genuine owner trade-off (`11` CD5-2).
- **Workstation installation.** No option or statement covers the installation burden that governed use on workstations
  implies under OP-7 (a)/(b) (RV5-M8).

### 2.4 Combinations

`03-HELDOUT-ATTACKS-RV5-D.md` §RV5-D-A06: 15 combinations; 10 change security and are not stated, or are stated
incorrectly; 5 are stated correctly.

## 3. Inputs the owner decision package will need (after correction)

1. OP-1 … OP-15 restated from the corrected rules and the completed calculator (CD5-4), with no choice made.
2. **The first-contact root trade-off** (CD5-1 options T1-a … T1-d), each with computed minimal sets for first admission and
   its availability consequence.
3. **The common-mode build-environment trade-off** (CD5-2 options E-a … E-c), merged with OP-10, each with computed minimal
   sets and cost.
4. The workstation installation consequence chosen by the architect under RV5-M8 (an administrator-protected install or
   pin, or C1–C2 anchoring on user-writable installs), stated in OP-7, OP-12 and OP-14.
5. OP-3 mode B stated with the per-update currency proof it requires.
6. For every option, the victim classes the statement covers (P1, P2, FA1, FA2, witness-reliant, CI record).
