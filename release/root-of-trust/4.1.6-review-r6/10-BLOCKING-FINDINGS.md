# 10 — Consolidated findings (review r6 synthesis D), CRITICAL to INFO

- **Revision reviewed:** RoT-1 revision 6, `4106885dadebac55596067a2586cf4d3097fc025`.
- **Panel verified:** reviewer B `512808695e8f3eb11187a8c70dc07e6783ad8395`, reviewer C `02bb90550342e8bb6d42ba636430ae3394d3a0f7`.
- **Synthesis run:** AR-0018.
- D-0008 and ARCH-0002 remain PROPOSED (`PROVISIONAL`, `in_effect: false`, no `chosen_option`). Nothing here approves them.

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 3 | RV6-H1, RV6-H2, RV6-H3 |
| MEDIUM | 6 | RV6-M1 … RV6-M6 |
| LOW | 12 | RV6-L1 … RV6-L12 |
| INFO | 2 | RV6-I1, RV6-I2 |

## Evidence classes

| Class | Meaning |
|---|---|
| **executed** | run in scratch by this review: the architect's reference executor `evidence/r6/gov_admit_reference_r6.py` (unmodified; real Ed25519 through OpenSSL; `sha256sum`), the pack checker `constitutional-surface/csi_check.py` (unmodified), the real Rust toolchain and C compiler (reviewer B's probe, re-run), real legacy binaries and real Git (reviewer C's probes, re-run) |
| **computed** | the architect's `CS6-derivation-calculator.py` loaded unmodified, with functions wrapped and the originals still called |
| **design** | pack text at `4106885` |

"B-Axx", "C-Axx" and "D-Axx" mean RV6-B-Axx, RV6-C-Axx and RV6-D-Axx. Every panel probe cited here was re-run by this review and
reproduced (`D-synthesis/01-REPRODUCTION.md`). Held-out attacks D-A01…D-A10: `D-synthesis/03-HELDOUT-ATTACKS-RV6-D.md`.

**No CRITICAL.**
- **Running machines with an anchor made before any compromise.** Registration, reproduction quorum, restrictor revocation,
  candidate and kernel binding, E7 restrictors and currency naming hold under every key-theft and pipeline shape tried. CS6,
  P4r6, FA6, CON6, ENV6, SRC6, ADM6, UW6, ATTR6, DA03r6, DA07r6, the register and statement checks, and the retained revision-5
  instruments were reproduced byte-identical (ADM6 and the CSI checks except run-dependent fields). B-A11 (352 machine rows,
  0 `current`) and B-A12 (246,608 key subsets, 0 accepts with ≤ 1 key) were reproduced byte-identical.
- **Each HIGH needs one of:**
  - control of the process that composes first-contact values, of the instructions that name the first-contact sources, or of
    the platform package submission;
  - a first-contact value that is stored, replayed or designated rather than read now;
  - the author of an environment manifest.

  None fails the chain for every machine without such a condition.

---

## RV6-H1 — HIGH — First-contact values are composed, designated and submitted by parties outside the stated first-contact root

**Summary.** The value that selects the lineage, the state and the evaluator at first contact (the first-contact manifest and
code, the list of sources and the procedure steps the operator follows, and under OP-13 (c) the platform package) has no rule
naming a party that establishes it at the authority the stated root confers:
- the trust-state publisher composes the manifest and code, and the designated sources only carry them;
- the source list and the procedure steps are printed by `gov trust fc-procedure`, which on a first-install machine can only be
  the carrier-delivered, unadmitted candidate;
- under OP-13 (c) "either suffices", whoever submits the package to the signing service selects the evaluator.

The declared first-contact root (`32` §6 FC-ROOT) and the consequence statements that rest on it are false.

**Origin:** RV6-B-H1 (composer), RV6-B-H2 (submitter part), extended by D-A01 (designation and procedure printer) and D-A01
part C (witness-reliant runners). **Adjudication:** CONFIRMED HIGH.

### Statement

1. **Composer.**
   - `07` §7 step 15: the `trust-state` external signer outputs "the first-contact manifest and code of the new state".
   - `30` R-PUB-4 and `06` §2 step 2: the owner publishes the code "in each designated source".
   - No rule has a source custodian (or media custodian) derive or check the manifest first-hand: `lineage_id` against the root
     ceremony record, `admitters` against the root-signed `bootstrap.admitter_digests`, `state_epoch` against a verified Trust
     State. `32` §9 names custodians and hosting, not who produces the value shown.
2. **Designation and procedure printer (D-A01).**
   - `32` §4, `06` §3 step 0 and the `09` header: "`gov trust fc-procedure` prints these steps for the owner's OP-13 answer".
   - `32` §10 FC-R2's bound: "the procedure prints each source's name and requires its page".
   - `31` GB-1′ lets an unadmitted RoT-1 binary run C0. `24` §4.2 does not list `fc-procedure` in any class.
   - `31` §9 TB-1′ rests on "the documented procedure never runs a candidate".
   - No rule states where the operator obtains the source list and steps. No RT substitutes them.
3. **Submitter.** `32` FC-3 under (c) "either": "the platform-signed package may replace FC-1 and FC-2". No rule names who builds
   or submits the package, or requires the signed admitter's digest to equal a root-signed admitter digest before signing. TA-13
   and A22 cover a compromised signing service, not an honest service signing what a submitter hands it.
4. **The procedure cannot distinguish these parties.** FC-1…FC-3 check agreement, manifest hash and admitter digest. They pass
   for any consistent set of pages the operator is directed to. A substituted evaluator then ignores FC-4…FC-8 (`32` §4, "What
   no code can enforce").
5. **Running machines.** Human confirmations, in-gate fingerprints and pins are "typed from an independent channel" (`24` §3.2).
   The witness service takes its input "from the owner's signing ceremony or the independent channel" (`24` §3.3). A value
   the publisher composes after its compromise selects the thief's descendant for P1, P2, CIR and WR machines.
6. **Pack statements contradicted.**
   - `32` §6 FC-ROOT; §7 (b) "one compromised source gives `FIRST_CONTACT_DISAGREEMENT`"; §10 FC-R1…FC-R3.
   - The generated FC-ROOT, FC-KEY-THEFT and FC-CONTENT blocks in `05` §3, `21` OP-13, `32` §6, `34` §4.
   - `31` §9 AD-1′ and TB-1′.
   - `25` §6 ("the one remainder that no mechanism removes is the first-contact root") and §7 (first-contact row; "never on P1").
   - `30` §10 and `21` OP-9-BYTES rows P1, P2k1, P2k2, WR and CIR.
   - `21` OP-6, OP-7 (c), OP-13 and §17.
   - D-0008 rules (16), (19) and (25).
   - FA6 S3 "executed minima equal CS6" (both omit the composer, the designation and the submitter).

### Evidence

- **executed** B-A01 part P (reproduced byte-identical). The publisher is compromised; every source is honest.
  - A substituted evaluator is admitted under OP-13 (a), (b), (c) "either" k = 1/2 and (d).
  - An attacker lineage with the genuine admitter is `ACCEPTED` under (a) and (b).
  - Under (c) "all" the result is `PLATFORM_SIGNATURE_INVALID`; with a package submitter, admitted.
  - Control, one compromised source under k = 2: `FIRST_CONTACT_DISAGREEMENT`.
- **executed** B-A01 part S (reproduced): under (c) "either", an honest signing service signs a submitter's substituted admitter.
  The procedure returns `OK` and the result is `ACCEPTED_BY_SUBSTITUTED_EVALUATOR`. Control (c) "all": `ADMITTER_DIGEST_MISMATCH`.
- **executed** D-A01 part P. Every owner source and the publisher are honest; the printed procedure names attacker pages.

  | OP-13 | Substituted evaluator, owner steps | Substituted evaluator, weakened steps | Genuine admitter, attacker pages show the genuine T7 code, candidate B7x (revoked at T9) |
  |---|---|---|---|
  | a, b, c_either_1, c_either_2 | `ACCEPTED_BY_SUBSTITUTED_EVALUATOR` | `ACCEPTED_BY_SUBSTITUTED_EVALUATOR` | `ACCEPTED` (state 7) |
  | c_all_1, c_all_2 | `PLATFORM_SIGNATURE_INVALID` | `ACCEPTED_BY_SUBSTITUTED_EVALUATOR` | `ACCEPTED` (state 7) |

  Controls:
  - designation known independently: genuine B8 `ACCEPTED` under every answer;
  - the current code with B7x: refused;
  - one owner page read beside one attacker page (k = 2): `FIRST_CONTACT_DISAGREEMENT`.
- **computed** D-A01 part C (CS6 wrapped; control reproduces the committed FC-ROOT block). With atom `desig` (the party that
  tells the operator which sources to read):

  | Variant | a | b | c_all_1 / c_all_2 | c_either_1 / c_either_2 | d |
  |---|---|---|---|---|---|
  | V1 sources only | {desig} | {desig} | {alt, desig} | {desig} | none |
  | V2 sources and steps | {desig} | {desig} | {desig} | {desig} | none |

- **computed** B-A01 part C (reproduced): `fcpub` is outside the declared root under every answer except (d) with first-hand media.
  - P1 gains {2 reproducer keys, transport, fcpub}.
  - P2k1, P2k2 and CIR gain the same set.
- **computed** D-A01 part C, witness-reliant runners (control reproduces the committed OP-9-BYTES WR row).
  - WR gains {2 reproducer keys, transport, fcpub} and {2 registration keys, 2 reproducer keys, fcpub}. Neither needs witness keys.
  - Content ingress (ING_WR) gains {2 registration keys, 1 verification key, pipeline, fcpub} and {2 registration keys,
    1 verification key, rc, rf, fcpub}.
- **design** as listed in the statement; D-A09 (the register names no composer, designation, printer or submitter).

### Failure scenarios

1. **Composer (B).** The owner chooses OP-13 (b). The host that signs Trust States and emits their manifests is compromised and
   emits a manifest naming a substituted `gov-admit`. Both custodians publish its code. Every first-install machine admits the
   attacker's TCB, while `21` states that one compromised source gives `FIRST_CONTACT_DISAGREEMENT`.
2. **Designation (D).**
   - A new engineer downloads `gov` and `gov-admit` from a release page and runs `gov trust fc-procedure`, as `06` §3 step 0
     suggests.
   - The carrier-supplied binary prints two look-alike "owner sources" and, under (c) "all", omits the signature step.
   - Both pages show a code over a manifest that names a substituted admitter. FC-1…FC-3 pass, and the substituted admitter
     installs the attacker's `gov`.
   - No owner source, key or signing service was touched.

### Unavoidable core versus this finding

| Situation | Determination |
|---|---|
| A machine with no prior trust accepts what its designated sources jointly show, and a human must already know where the owner publishes | core; stated as OP-13 and TA-5′ |
| The sources show a value one publisher composed and nobody else established | **not core**: each source custodian can derive the manifest from root-signed facts, or lineage and admitter set can come from a root-ceremony record the publisher cannot compose |
| The list of sources and the procedure steps come from a carrier or the unadmitted candidate | **not core**: the designation can be part of the root ceremony record delivered out of band, and no unadmitted binary need print anything that selects |
| The package signed under (c) is whatever a submitter hands the service | **not core**: submission can be performed or authorised at the registration authority, with the package digest checked against the root-signed admitter list before signing |
| Anchors typed, pinned or witnessed from a value the publisher composes | **not core** for lineage and admitter; for the state fingerprint, first-hand derivation by the channel custodian or a stated root atom |

### Why HIGH

- TCB compromise on first-install machines below the declared root with no key, under every code-path OP-13 answer. That
  includes (b) and, through the designation with weakened steps or a submitter, (c) "all".
- False consequence statements for security-material options (the BC5-4 class).

**Not CRITICAL:** machines anchored before the compromise are unaffected; each route needs the publisher host, a carrier plus an
operator who follows the printed procedure, or the submission role.

### Class and novelty

**Narrowed remainder of BC5-1** (R2-H2/BC-2 ∩ R2-H3/BC-3), in the pass-through shape of FD-1 §2 (3) applied to first-contact
sources and procedure inputs. The instances (composer, designation and printer, submitter) are new. Consolidated class
**BC6-1** (`11-CORRECTION-DELTA.md`).

---

## RV6-H2 — HIGH — First-contact currency is unbounded: stored, replayed or designated values select stale state, also over a store that holds newer state

**Summary.**
- The state selected at first admission is whatever epoch the typed code's manifest names, and `valid_until` is optional.
- A replayed package (OP-13 (c) "either"), provisioning media (d), codes stored in a CI image, or a stale or attacker-designated
  page select an old genuine Trust State. In that state a binary since revoked, including a known-malicious one, is published
  and not revoked.
- Re-admission keeps the verifier trust store but reads none of it. A machine that holds the revocation, and an anchor above
  the selected state, admits the revoked binary.

**Origin:** RV6-B-H2 (replay part), extended by D-A02 (re-admission), D-A08 (media and CI images) and D-A01 S2 (designated
pages). **Adjudication:** CONFIRMED HIGH.

### Statement

1. **No mandatory age.**
   - `32` §3: `valid_until` "(optional)"; `schemas/first-contact-manifest.schema.json` does not require it.
   - `32` §7 states the bound under (c) as "the FCM's `valid_until`".
   - DR-04 claims currency "now (bounded by issued_at and valid_until)".
2. **Stored values.**
   - `32` §7 (d): media carry "code, FCM and admitter".
   - `32` §8 and `06` §3: CI images use "codes and FCM provisioned by the image operator". The image record's `valid_until`
     (`31` R-ADM-7′) bounds the record, not the manifest's age.
   - `32` §10 FC-R4's bound is "media custody"; RS-B1 names only "a stale page".
3. **Re-admission ignores the store.**
   - `31` R-ADM-8′: re-admission "keeps the store: anchors, clock and accepted-TBM high-waters, per-project records".
   - R-ADM-3′ and `25` §5 give bootstrap mode no store input.
   - No rule refuses a first-contact epoch below the store's anchor, or a candidate the store holds as revoked.
   - Contradicted: `31` §2 ("no admission discards the monotonic state of an earlier one"), in effect; D-0008 rule (7) ("negative
     facts are sticky") on that machine; RS-B1's bound ("the admitted binary anchors next"), which a malicious binary never
     honours.
4. **Genuine versus malicious.** A genuine revoked binary restricts itself when its store holds the negative (GB-3). A malicious
   revoked binary ignores every rule (TB-1′). Its admission record is written.

### Evidence

- **executed** B-A01 part R (reproduced byte-identical). The old platform package has the T7 manifest and no `valid_until`.
  - Genuine B7 and malicious B7x (both revoked at T9) are `ACCEPTED`.
  - Controls: an expired `valid_until` gives `FIRST_CONTACT_MANIFEST_EXPIRED`; the current code refuses B7x.
- **executed** D-A02 (reference executor).
  - First admission of B9 at T11; the store is given anchor 11, the accepted-TBM high-water (2, 1, 10) and T11, which revokes B7
    and B7x. The record then expires.
  - Re-admission with the T7 value: B7x `ACCEPTED` under (a)/(b) and under (c) "either"; selected state 7.
  - The store is kept, with anchor 11 and the held revocation of B7x.
  - The genuine B7, re-admitted the same way, runs C2 as `BINARY_REVOKED_SELF` (GB-3).
  - Control: the current code with B7x is refused.
  - Code: `accept` has no store parameter. No rule and no RT covers this (RT-170 covers E10 only).
- **executed** D-A08 (reference executor).
  - (d) media prepared at T7 and used on 2026-09-14: B7x and B7 `ACCEPTED`.
  - Codes provisioned into a CI image at T7: B7x `ACCEPTED`.
  - Controls: `valid_until` 2026-06-01 gives `FIRST_CONTACT_MANIFEST_EXPIRED`; current media refuse B7x.
- **executed** D-A01 S2: attacker-designated pages showing the genuine T7 code make the genuine admitter accept B7x under every
  code-path answer, including (c) "all".
- **computed** CS6 models no "revoked binary admitted at first admission" goal (B-A01 part C; D-A04): no calculator block covers
  this class.

### Failure scenario

- Revoked B7x is the published output of a reproducer-key compromise that T9 remediated.
- **Replay route.** Under OP-14 (b), a workstation's admission record expires. At re-admission a proxy or package mirror serves
  the T7 admitter package (under (a)/(b), a cached T7 page). B7x is admitted and installed. The machine's own store held its
  revocation.
- **Media route.** A media batch prepared in May provisions a designated machine in September. B7x is again the first TCB.

### Why HIGH

- HO-0001 §3.2's forbidden outcome: attacker-selected stale signed state becomes a current trusted fact, here the TCB.
- The route needs a carrier, stored media or a designated page, and no key. On re-admitted machines it defeats monotonic state
  the machine already holds.
- The stated bounds are optional or absent.
- Precedent: revoked and remediated first binaries were HIGH in review r4 (RV4-H2).

**Not CRITICAL:** it requires a past remediated compromise, or a genuine defect, whose binary remains published in an older state.

### Unavoidable core versus this finding

| Situation | Determination |
|---|---|
| A machine that never received a revocation, whose owner source is itself stale, cannot know it | core, **once the staleness is bounded** by a mandatory maximum age and shown |
| A stored or replayed value of unbounded age selects the state | **not core**: a mandatory `valid_until` with a compiled maximum, or a code read now, bounds it |
| A machine that holds newer anchors and negatives admits an older state | **not core**: the store is present, and bootstrap mode can apply it |

### Class and novelty

**Narrowed remainder of BC5-1** at its intersection with R2-H2/BC-2 (currency). The instances (replayed package, media, CI codes,
designated pages, re-admission over a newer store) are new, and revision 6 introduced the package and media paths. Consolidated
class **BC6-2**.

---

## RV6-H3 — HIGH — No party establishes the environment manifest; its author selects every production binary's bytes

**Summary.**
- The manifest's component selection, placement, recipe, assembly tool, upstream checksum key and supplier-class label have no
  establishing party.
- Environment reproducers reproduce what the manifest says; binary reproducers re-assemble the same recipe.
- Under OP-16 (a) and (b), the manifest's author (the pipeline in a conforming process) selects the bytes of every production
  binary. OP-16 (b) counts diversity by label.

**Origin:** RV6-B-H3, extended by D-A05 E1. **Adjudication:** CONFIRMED HIGH.

### Statement

- `33` §3–§5, R-BENV-1…R-BENV-5; `schemas/environment-manifest.schema.json` (`upstream_checksum_reference` and `assembly.tool` are
  free strings; `supplier_class` is one letter).
- R-BENV-1 checks listed digests against "a checksum signed by that component's upstream release". It does not say which key is
  trusted, which components are selected, or what the recipe adds.
- R-BENV-2 establishes that the tree follows from the manifest, not that the manifest was legitimately chosen.
- R-VER-1's verifiers check components, not the recipe.
- DR-13 gives the manifest's authority to the two reproductions that carry it.

Contradicted: `33` §2 (1)–(3), §6 OP-16-ENV, §7 INV-ENV-PIPELINE, §8 TB-S2′; `21` OP-16 and §17; `25` §7 ("the pipeline
supplying the build image or environment record | no"); `30` §2 F-ENV; `01` G25; D-0008 rules (9) and (26).

### Evidence

- **executed** B-A02 (reproduced byte-identical; real `rustc 1.98.1`):
  - A07a recipe injection: `REGISTERED`, bit-identical injected binaries, `ACCEPTED`.
  - A07b placement of genuinely signed instrumented components: `ACCEPTED`.
  - A07c the same recipe in both OP-16 (b) classes: `ACCEPTED`.
  - A08 two labels over one compromised upstream: `ACCEPTED`.
  - A09 an upstream key named by the manifest: `ACCEPTED`.
  - Controls: pinned keys give `ENVIRONMENT_COMPONENT_UNVERIFIED`; honest recipes with class A compromised give
    `REPRODUCTION_CONFLICT`.
- **computed** B-A02 (reproduced): with a pipeline-authored manifest, {pipeline} is minimal under OP-16 (a) and (b) for n2q2 and
  n3q2, and INV-ENV, INV-ENV-PIPELINE and INV-ONE fail. With labels, INV-ENV-B fails. OP-16 (c) is unaffected.
- **computed** D-A05 E1: {pipeline} stays minimal under OP-16 (a) and (b) with OP-9 (d) (custodians' own reproduction), OP-8 = 2,
  OP-2 (b), victim FA under OP-13 (b), and victim CIR. OP-16 (c) is unaffected. Control: {pipeline} is never minimal.

### Why HIGH

TCB compromise below the declared minimum from an input with no assigned authority, under two of three OP-16 answers and every
other owner answer computed; the OP-16 statements and rule (26) are false. **Not CRITICAL:** OP-16 (c) holds, and a process that
authors manifests outside the pipeline is possible (no rule requires it).

### Class and novelty

**Narrowed remainder of BC5-2** (BC4-1/R2-H3). Revision 6 moved the unestablished selector from the image digest to the manifest
content. Consolidated class **BC6-3**.

---

## MEDIUM

| ID | Statement | Evidence | Origin → adjudication | Carriable? |
|---|---|---|---|---|
| **RV6-M1** | The generated CONTENT block prints the repository-writer atom `repo` as "1 reproducer key" in 8 of its 24 rows (`21`, `34`), and `statements_check.py` S1 compares rendering with rendering. D extension: over the whole atom vocabulary only `repo` is misrendered. The invariant classifier `rep` also misclassifies `repo`, but no invariant that uses it runs on a goal containing `repo`, so the calculator's sets and invariants are correct. | computed B-A03 (reproduced byte-identical); computed D-A06 (the control renderer reproduces the committed statements; the corrected renderer changes exactly 8 CONTENT rows) | RV6-B-M2 → CONFIRMED MEDIUM | the fix is mechanical; it belongs to BC6-4's statement-derivation closure (`11` CD6-4) |
| **RV6-M2** | **Register completeness is checked over rule ids, not over inputs.** `register_check.py` C2 requires every rule id of the scoped tables to belong to a decision; it reads no schema and no procedure input. D extension (D-A09, lexical lower bound): of 251 leaf fields of 16 revision-6 schemas, 193 are named nowhere in the register and 28 are named in a selector entry whose authority text names no establishing party. The register names no manifest composer, source designation, procedure printer, package submitter or environment-manifest author. D-A04: none of 15 review-r6 defects has a plan row, a register row and a detecting instrument together, and RT-128, RT-131, RT-159, RT-162 and RT-183 have no input independent of the register. | computed B-A16 (reproduced); computed D-A09, D-A04 | RV6-B-M3 → CONFIRMED MEDIUM, extended | **no**: the mechanism is architecture (`29` §4–§5.5, R-SEL-1); its correction is blocking class BC6-4 |
| **RV6-M3** | The first-install layout migration and the exchange-to-journal window lie outside the journal phase model. The documented recovery leaves half-migrated trees `LEGACY`, `PARTIAL` or `ABSENT`; on those trees legacy `init --force` serves restricted material. D extension (D-A10): the `ABSENT` condition ignores an existing overlay or views directory; `init` is not in `19` §9's coverage list; no R-INIT rule and no RT addresses an existing overlay. C's escalation condition (an `init` that overwrites or ignores the overlay turns this into a silent classification loss) is therefore open in the text. | executed C-A15 `crashmig6` (reproduced byte-identical); design D-A10 | RV6-C-M2 → CONFIRMED MEDIUM | yes: CR6-C-7 plus a normative `init` rule (`11` §6) |
| **RV6-M4** | The per-project record's identity (path and/or `project_trust_id`) is defeated by a worktree, a move, a second clone, a fork or a template copy: E10 and strength detection are lost, or two projects share one record. | executed fact `ptid-duplication` (C); design | RV6-C-M3 → CONFIRMED MEDIUM | yes: CR6-C-8 |
| **RV6-M5** | Contradictory re-record rules at install commit let a remedy or an update clear a strength report or a pending `policy_lowering`/`registration_change` gate. | design (C) | RV6-C-M4 → CONFIRMED MEDIUM | yes: CR6-C-9 |
| **RV6-M6** | The admission store and the account verifier trust store are specified two incompatible ways. D extension (D-A07): the record that decides "first admission" is any unsigned file in the store. Pre-admission same-account code that plants one suppresses the move-aside, and its planted anchor, per-project record and trust-gate confirmation survive a genuine first admission (control: without the planted record the store is moved aside). AD-2's bound depends on that file. | design (C); executed D-A07 (reference executor); C `admtx6` (reproduced byte-identical) | RV6-C-M5 → CONFIRMED MEDIUM, extended | yes: CR6-C-10, plus a first-admission determination that does not rest on a file the governed account can write (`11` §6). A3 can write an account store after admission too (RS-3), so no trust relationship changes. |

## LOW

| ID | Statement | Evidence | Origin → adjudication |
|---|---|---|---|
| RV6-L1 | R-CON-5 lists only units matched by a compiled name or path-prefix list, or by an optional inventory flag. `COMMAND_CONTRACT`, overlay templates and taxonomy are not listed. D extension (forward compatibility): new kernel-shipped files for Gate W and the G0–G6 scheduler at paths outside the prefix list are classified by inventory data alone (check exit 0), and default deny holds (exit 2 without a row). A weakened proposal is refused first-hand (exit 3). The change is **not** listed without the flag (exit 0), and is listed with it (exit 8). Selection is unaffected. | executed B-A10 (reproduced); executed D-A03 | RV6-B-L1 → CONFIRMED LOW, extended |
| RV6-L2 | Stale revision-5 text in `05` §1–§2. | design | RV6-B-L2 → CONFIRMED LOW |
| RV6-L3 | Verification precedes environment registration; the verifier's environment source is unstated (inside BC6-3's correction). | design | RV6-B-L3 → CONFIRMED LOW |
| RV6-L4 | Derivation-tool provenance at the registration ceremony is unstated. | design | RV6-B-L4 → CONFIRMED LOW |
| RV6-L5 | `gov-admit` does not apply the kept accepted-TBM high-water at re-admission, and a rollback to an admitted lower-TBM binary keeps its record. At use, `09` R-ART-2 refuses trusted operations below the high-water (`BINARY_T0_ROLLBACK`), so the outcome fails closed. The reference executor's `gov_run` does not implement R-ART-2 (it returns `ALLOWED`), so no shared vector carries it. `31` R-ADM-7′, `20` and RT-170 omit the consequence. | executed B-A04 and D-A02 (reference); design `09` R-ART-2 | RV6-B-M1 → CONFIRMED, **re-rated LOW** (R-ART-2 refuses at use; the held-negative and anchor part of the same root cause is HIGH in RV6-H2); RV6-C-L6 → DUPLICATE, consolidated here |
| RV6-L6 | Out-of-project ignore sources re-drop the migration occupation (fail closed). The condition is stated and doctor names the source; the remedies' force-add of the occupation is not stated for `kernel reinstall`. | executed C `gitops6` (reproduced) | RV6-C-M1 → CONFIRMED, **re-rated LOW** (condition stated exactly, detection specified; availability only) |
| RV6-L7 | `.git/info/attributes` overrides the `.gitattributes` member (fail closed). | executed C (reproduced) | RV6-C-L1 → CONFIRMED LOW |
| RV6-L8 | The transaction-area foreign-artefact scan does not exclude the `done/` archive (fail safe). | executed and design (C) | RV6-C-L2 → CONFIRMED LOW |
| RV6-L9 | `gov-admit` reference edges: a record-less store with anchors is moved aside; records are honoured by digest across lineage stores; the store-name prefix length is unfixed. | model C `admtx6` (reproduced byte-identical) | RV6-C-L3 → CONFIRMED LOW |
| RV6-L10 | A third subtree litter location, `governance/overlay/spec`, stays `COMPLETE` unnamed. | executed C matrix | RV6-C-L4 → CONFIRMED LOW |
| RV6-L11 | Evidence and text accuracy: the LAY6 `INFOATTR` row does not exercise its condition; "30,735 writing rows"; `props6` input; the `20` §5 `committed` phase; `08` §2's signed-file sentence. | executed and design (C) | RV6-C-L5 → CONFIRMED LOW |
| RV6-L12 | `21` §17 states OP-10 (a) + OP-16 (a) but not OP-16 (b) + OP-10 (a). Under the latter, {toolchain_up} alone still yields malicious bytes; environment diversity does not cover the toolchain archive. | computed D-A05 E2 | NEW (D) → LOW (option statement) |

## INFO

| ID | Statement | Origin |
|---|---|---|
| RV6-I1 | The acting role remains caller-declared; no trust gate depends on it (`27` §5). | RV6-B-I1 (RV5-I1) |
| RV6-I2 | Derived members of an owner binding group (the Capability Acceptance Contract's compiled YAML) are carried to the capability-contract phase as RT-182. | RV5-I2, carried |
