# 01 — Findings (review r6 B, trust and security)

- **Revision reviewed:** RoT-1 revision 6, `4106885dadebac55596067a2586cf4d3097fc025`: `release/root-of-trust/4.1.6/`,
  `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`.
- **Reviewer:** AR-0016, role `rot-reviewer-trust-security`.
- This reviewer does not issue the architecture verdict.

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 3 | RV6-B-H1, RV6-B-H2, RV6-B-H3 |
| MEDIUM | 3 | RV6-B-M1, RV6-B-M2, RV6-B-M3 |
| LOW | 4 | RV6-B-L1 … RV6-B-L4 |
| INFO | 1 | RV6-B-I1 (RV5-I1 unchanged) |

## Evidence classes

| Class | Meaning |
|---|---|
| **executed** | run in scratch: the architect's reference executor `evidence/r6/gov_admit_reference_r6.py` (unmodified; real Ed25519 through OpenSSL; `sha256sum` as the platform hash tool), the pack checker `constitutional-surface/csi_check.py` (unmodified), the real Rust toolchain (`rustc 1.98.1`) and system C compiler |
| **computed** | the architect's `CS6-derivation-calculator.py` or `P4r6-conformance-oracle.py` loaded unmodified, with functions wrapped and the originals still called; or this review's brute-force search over CS6's acceptance function |
| **design** | pack text at `4106885` |
| **code** | a reference instrument's source, or 4.1.5 runtime (unchanged since `da9c851`) |

"A-nn" means held-out attack RV6-B-A-nn (`02-HELDOUT-ATTACKS.md`). Outputs are under `evidence/outputs/`.

**No CRITICAL.**
- **Running machines with a compiled lineage.** Registration, reproduction quorum, restrictor revocation, candidate and kernel
  binding, E7 restrictors and currency naming hold under every key-theft and pipeline shape this review tried. CS6, P4r6,
  FA6, CON6, ENV6, SRC6 and the retained revision-5 instruments were re-run byte-identical.
- **Each HIGH needs one of:**
  - control of the process that composes first-contact values;
  - a pipeline or submitter role the pack names but does not govern;
  - a carrier replaying a signed package, under one owner answer.

  None fails the chain for every machine without such a condition.

---

## RV6-B-H1 — HIGH — The first-contact code is composed by the trust-state publisher; the designated sources only carry it

**Summary.**
- One rank-3 party selects the lineage, the state and the evaluator on every first-install machine. This holds under OP-13
  (a), (b), (c) "either" and (d) when media carry the published code.
- The same party selects the currency input of P1, P2 and CIR machines.
- The declared first-contact root, and the first-contact and OP-9 consequence statements, are false.

### Statement

1. **Who composes the first-contact values.**
   - `07` §7 step 15: the `trust-state` external signer outputs "`trust-state.dsse.json`; the **first-contact manifest and
     code** of the new state (`32` §3) and the state fingerprint published in the independent channels".
   - `30` R-PUB-4, publisher section: "The first-contact code and state fingerprint of every TSS are published in the
     independent channels".
   - `06` §2 step 2: "For every new Trust State the owner publishes the first-contact manifest (any carrier) and its code (in
     each designated source)".
2. **No rule makes a source establish the value it carries.** No custodian of a source, or of media, is required to derive or
   check the manifest first-hand. That would mean checking:
   - `admitters` against the root-signed `bootstrap.admitter_digests`;
   - `lineage_id` against the root ceremony record;
   - `state_epoch` against a verified Trust State.

   `32` §9's custody record names each source's custodian and hosting, not the producer of the value it shows. A text search
   of `06`, `31` and `32` finds no such rule.
3. **What the procedure checks.**
   - FC-1…FC-3 check that the codes agree, that the manifest hashes to the code, and that the admitter digest is the one the
     manifest names.
   - FC-4…FC-8 run inside the evaluator the procedure has just selected.
   - A manifest naming a substituted admitter passes FC-1…FC-3 whenever every source shows its code. The substituted
     evaluator then ignores FC-4…FC-8 (`32` §4, "What no code can enforce").
4. **Consequence.** At first contact, the selector of lineage, state and evaluator is the party that composes the manifest:
   the trust-state signer or publisher, rank 3 in `29` §3. The sources are carriers of its value.
   - This is the pass-through shape of FD-1 §2 (3), applied to sources instead of signatures.
   - `29` DR-06 names "admitters[target] of the manifest bound by the agreed code … the admitter digest is registered and
     reproduced (rank 1 or 2)". No party establishes that second clause when the manifest is composed.
5. **Running machines take the same value.**
   - Human confirmations and in-gate fingerprints are "typed from an independent channel" (`24` §3.2), and pins are
     provisioned from it.
   - A fingerprint that the publisher composes for a descendant it signed selects that descendant for P1 (a confirmation or
     pin made after the compromise), P2 and CIR machines.
6. **The instruments cannot see it.**
   - CS6 `srcs(C, k)` requires `ch1`/`ch2`.
   - `thief_selectable` never selects for P1 while `V_P1_NAMES_STATE` holds.
   - FA6 shows the attacker's code on a page only when that page's `ch` capability is held.
7. **Pack statements contradicted.**
   - `32` §6 FC-ROOT and §10 FC-R1 ("exactly the root sets of §6").
   - The generated FC-ROOT, FC-KEY-THEFT and FC-CONTENT blocks in `05` §3, `21` OP-13, `32` §6 and `34` §4.
   - `32` §7 (b): "one compromised source gives `FIRST_CONTACT_DISAGREEMENT`".
   - `31` §9 AD-1′.
   - `25` §6 ("The one remainder that no mechanism removes is the first-contact root").
   - `25` §7 rows "the first-contact sources of the OP-13 answer (no key)" and "q reproducer keys + trust-state key + the
     victim's currency input … never on P1".
   - `30` §10 and `21` OP-9-BYTES rows P1, P2k1, P2k2 and CIR.
   - `21` OP-6 ("The lineage confirmed is the one the first-contact root selects").
   - D-0008 rules (16), (19) and (25).
   - `22` §2 BC5-1 row.
   - FA6 S3 "executed minima equal CS6". Both omit the composer.

### Evidence

- **executed** `RV6-B-A01-first-contact-selectors.json` part P.
  - Instruments: reference executor r6 unmodified; FA5 world transformed exactly as FA6 S1.
  - Setup: the publisher is compromised. Every designated source is honest, uncompromised and republishes the code it
    receives. No key other than the publisher's is used.

  | OP-13 | Honest control | Publisher names a substituted admitter | Publisher names an attacker lineage, genuine admitter | Honest publisher, one compromised source (k = 2) |
  |---|---|---|---|---|
  | a | `ACCEPTED` | **`ACCEPTED_BY_SUBSTITUTED_EVALUATOR`** | **`ACCEPTED`** | — |
  | b | `ACCEPTED` | **`ACCEPTED_BY_SUBSTITUTED_EVALUATOR`** | **`ACCEPTED`** | `FIRST_CONTACT_DISAGREEMENT` |
  | c_all_1 | `ACCEPTED` | `PLATFORM_SIGNATURE_INVALID` (with a package submitter, H2: admitted) | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | — |
  | c_all_2 | `ACCEPTED` | `PLATFORM_SIGNATURE_INVALID` (with a package submitter: admitted) | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | `FIRST_CONTACT_DISAGREEMENT` |
  | c_either_1 | `ACCEPTED` | **`ACCEPTED_BY_SUBSTITUTED_EVALUATOR`** | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | — |
  | c_either_2 | `ACCEPTED` | **`ACCEPTED_BY_SUBSTITUTED_EVALUATOR`** | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | `FIRST_CONTACT_DISAGREEMENT` |
  | d (media from the published code) | `ACCEPTED` | **`ACCEPTED_BY_SUBSTITUTED_EVALUATOR`** | `FIRST_CONTACT_LINEAGE_NOT_COMPILED` | — |

- **computed** part C. CS6 is unmodified, with `srcs`, `fc_eval_sub`, `atoms_for` and `thief_selectable` wrapped.
  - Added atom: `fcpub`, the first-contact publisher process, which implies `ts`.
  - Control: with the wrapper off, the FC-ROOT rows equal the committed generated block.

  **First-contact root sets:**

  | OP-13 | Declared first-contact root | No-key sets the declared root omits |
  |---|---|---|
  | a | {ch1} | **{fcpub}** |
  | b | {ch1, ch2}; {ch1, op1src} | **{fcpub}** |
  | c_all_1 | {alt, ch1} | {alt, fcpub}; with the submitter atom of H2: {ch1, submit}; {fcpub, submit} |
  | c_all_2 | {alt, ch1, ch2}; {alt, ch1, op1src} | {alt, fcpub}; {ch1, ch2, submit}; {ch1, op1src, submit}; {fcpub, submit} |
  | c_either_1 | {alt}; {ch1} | **{fcpub}**; {submit} |
  | c_either_2 | {alt}; {ch1, ch2}; {ch1, op1src} | **{fcpub}**; {submit} |
  | d | {media} | **{fcpub}** if media carry the published code; none if media are derived first-hand |

  **Running victims** (OP-9 n2q2), with the anchoring event made after the compromise:

  | Victim | Committed statement | Sets with `fcpub` |
  |---|---|---|
  | P1 | {2 reproducer processes} | **{2 reproducer keys, transport, fcpub}**; {2 registration keys, 2 reproducer keys, fcpub} |
  | P2k1 | …; {2 reproducer keys, transport, ts, ch1} | adds {2 reproducer keys, transport, fcpub} |
  | P2k2 | …; {2 reproducer keys, transport, ts, ch1, ch2} | adds {2 reproducer keys, transport, fcpub} |
  | CIR | …; {2 reproducer keys, transport, ts, pinprov} | adds {2 reproducer keys, transport, fcpub} |
  | content ING_P1 | {insider}; …; {2 registration custodians, 1 verification key, rc, rf} | adds {2 registration keys, 1 verification key, rc, rf, fcpub} |

- **design** `07` §7; `30` R-PUB-4; `06` §2; `32` §3, §4, §6, §7, §9, §10; `29` §3, DR-06; `24` §3.2; `01` A20, TA-5′; `05` §9
  (playbooks cover a compromised source and a stolen trust-state key, not a compromised publisher of codes).

### Failure scenario

1. The owner chooses OP-13 (b): the owner's website and a signed mailing list, under distinct custody. `21` states that one
   compromised source then gives `FIRST_CONTACT_DISAGREEMENT`.
2. The online host that signs Trust States and emits their manifests and codes is compromised.
3. At the next Trust State the host emits a manifest with the genuine lineage and state, and the digest of a substituted
   `gov-admit`. Both custodians publish its code, as they do every release.
4. A new engineer runs FC-1…FC-3. The two codes agree, the manifest hashes to them, and the downloaded `gov-admit` matches.
   The engineer runs it. It installs the attacker's `gov` and writes an admission record.
5. Every machine installed until detection has an attacker TCB.
6. An administrator who meanwhile types the newly published fingerprint into `confirm-state` on a running machine anchors the
   thief's descendant. With two stolen reproducer keys and transport, `verify-artifact` then accepts a malicious binary on
   that P1 machine.

### Why HIGH

- **TCB compromise below the declared threshold.** The first TCB of every first-install machine falls to one rank-3 party with
  no other key, under five of seven OP-13 answers. The declared root requires two independently held sources under (b).
- **False statements.** The first-contact and OP-9 consequence statements are false: the BC4-4/BC5-4 class.
- **Not core** (next table).

### Unavoidable core versus this finding

| Situation | Determination |
|---|---|
| A machine with no prior trust accepts what its designated sources jointly show | core; stated as OP-13 |
| The sources show a value one publisher composed and nobody else established | **not core**: each source custodian, or the root ceremony for lineage and admitter list, can establish the value first-hand from root-signed facts before publishing |
| Anchors typed or provisioned from a publisher-composed fingerprint | **not core** for the admitter list and lineage. For the state fingerprint: the same first-hand derivation by the channel custodian from a verified TSS, or a statement of the composer as a root atom with its computed sets |

### Class and novelty

- **Narrowed remainder of BC5-1 (RV5-H1).** The pass-through shape of FD-1: a selector whose value is carried, not
  established, by the parties that confer its authority.
- **The instance is new.** Revision 5's instance was one page selecting; this one is one composer selecting what every page
  shows.
- **Lower-trust input:** the trust-state publisher process (rank 3).
- **Higher-trust fact:** the root of trust, the evaluator and the first TCB on a machine.

### Correction direction (architectural)

1. **First-hand first-contact values.** Every designated source (and media custodian) publishes only a code over a manifest
   it derived itself:
   - `lineage_id` from the root ceremony record;
   - `admitters` from the root-signed Trust Policy;
   - `state_epoch` from a Trust State it verified with an admitted binary.

   Alternatively, lineage and admitter set come from a root-threshold statement that the publisher cannot compose.
2. **Register and calculator.** Add a register row for "first-contact value composition" with its selector and authority. Add
   a calculator atom for the composer, used for FA, P1, P2 and CIR victims.
3. **Restated statements.** Regenerate FC-ROOT, FC-KEY-THEFT, FC-CONTENT, OP-9-BYTES and `25` §7 from that calculator.
4. **Acceptance test.** A compromised publisher with honest sources, under every OP-13 answer.

---

## RV6-B-H2 — HIGH — Under OP-13 (c) "either suffices", the platform path's selectors lie outside the declared root

**Summary.** The package submitter and a carrier replaying an old genuine package are both selectors the declared root omits.
- The submitter admits a substituted evaluator.
- The replay admits revoked binaries, including a known-malicious one, as the first TCB.
- `valid_until` is not required.
- FA6 exercises neither path.

### Statement

1. **The path.**
   - `32` FC-3: "Under (c) 'either suffices', the platform-signed package may replace FC-1 and FC-2: its admitter carries
     the compiled lineage and the owner's FCM of its build".
   - `32` §7: "The state selected is the epoch of the FCM compiled into the admitter package … The bound is the FCM's
     `valid_until`".
   - `32` §3 lists `valid_until` as optional, and `schemas/first-contact-manifest.schema.json` does not require it.
2. **What selects on this path.**
   - **(i) The package bytes, chosen by whoever builds and submits the package.** No rule names that party. No rule requires
     the signed admitter's digest to equal the root-signed `bootstrap.admitter_digests` before signing. TA-13 and A22 cover
     a compromised signing service, not an honest service signing what a submitter hands it.
   - **(ii) The package's FCM (state), whose age is chosen by whichever signed package a carrier delivers.** Nothing bounds it
     when `valid_until` is absent. The admitted binary anchors later only if an operator performs `confirm-state`; under
     OP-7 (d) it never needs to.
3. **Evaluator binding does not help.** A substituted admitter ignores FC-8, and a genuine old admitter checks FC-8 against the
   stale state it was given.
4. **The instruments never test either selector.**
   - The reference executor never reads `compiled_fcm`: two occurrences, the constant and its comment.
   - FA6's platform-only branch types the current genuine code and passes the current genuine manifest:
     `run_accept(binary, [gfcc] * k, stmts, dict(compiled, compiled_fcm=gmb), fcm=gmb)`.
   - FA6 assumes the service signs only the genuine admitter: `signed = (adm == ADM_BYTES) or ("alt" in caps)`.
   - S3's equality for `c_either_*` therefore holds by construction.
5. **Unspecified construction.** An admitter that compiles "the FCM of its build" cannot list its own digest in that FCM's
   `admitters`, because the digest depends on the FCM. FC-8 nonetheless requires the FCM's admitter set to equal the Trust
   Policy list containing the running admitter.
6. **Pack statements contradicted.**
   - `32` §6 FC-ROOT rows `c_either_1` and `c_either_2`.
   - `32` §7 currency paragraph (the "bound").
   - `32` §10 FC-R3 ("inside FC-R1 (`alt`)") and RS-B1 as restated.
   - `21` OP-13 (c) ("'either' adds the path as a root on its own").
   - `21` §17 ("OP-13 (c) 'either' + any OP-9 | the signing path is a first-contact root on its own").
   - `25` §2 platform code-signing row.
   - FA6 S3 `c_either_*` equality.
   - D-0008 rule (25).

### Evidence

- **executed** `RV6-B-A01-first-contact-selectors.json` part R (replay) and part S (submitter).
  - Instruments: reference executor r6 unmodified; FA5 world.
  - World: at T7, B7 (genuine) and B7x (produced with keys p1–p3, which root v2 later rotates out) are published. Both are
    revoked at T9. T10 is current.

  | Row | Result |
  |---|---|
  | platform-only procedure on the old genuine package | `OK` |
  | R1 old package FCM (T7, issued 2026-05-01, no `valid_until`), candidate B7, bundle without the conflicting reproductions | **`ACCEPTED`** |
  | R2 same FCM, candidate **B7x (malicious)**, bundle without the genuine reproductions | **`ACCEPTED`** |
  | R3 control: same FCM with `valid_until` 2026-06-01, now 2026-09-14 | `FIRST_CONTACT_MANIFEST_EXPIRED` |
  | R4 control: current code (T10), full bundle, B7x | `BINARY_REVOKED` |
  | R5 control: current code (T10), old bundle, B7x | `STATE_NOT_HELD_OR_FINGERPRINT_MISMATCH` |
  | S `c_either_1`, `c_either_2`: honest service signs a submitter's substituted admitter carrying the genuine lineage | procedure `OK`; **`ACCEPTED_BY_SUBSTITUTED_EVALUATOR`** |
  | S control `c_all_1`: the same package against the genuine code | `ADMITTER_DIGEST_MISMATCH` |

- **code** part I: `executor_accept_reads_compiled_fcm: false`, `FA6_platform_only_branch_passes_current_genuine_manifest:
  true`, `FA6_assumes_platform_signs_only_the_genuine_admitter: true`.
- **computed** part C: under `c_either_1` and `c_either_2`, {submit} is a no-key set outside the declared root. Replay has no
  CS6 goal: CS6 models no "revoked binary admitted" goal at first admission.
- **design** `32` §3, FC-3, §7, §10; schema; `01` TA-13, A22; `05` §9 ("withdraw the path's packages" leaves already-signed
  copies valid); `21` OP-13, §17; `25` §2.

### Failure scenario

1. The owner chooses OP-13 (c) "either suffices" so that developers can install `gov-admit` from a platform store.
2. **Submitter route.** Release CI builds and submits the packages with the developer signing credential. A compromised CI job
   submits a substituted admitter with the genuine compiled lineage. The service signs it, and new machines admit the
   attacker's TCB with no source or signing-service compromise.
3. **Replay route.** A package mirror, proxy or the platform's own archive serves the admitter package built at T7. B7 was
   revoked at T9 for a C3 enforcement defect, and B7x was the output of the key compromise that T9 remediated. A first-install
   machine admits B7x from that package. Under OP-7 (d) it runs governed work labelled `FRESHNESS_UNPROVEN`. B7x is
   malicious and ignores every later rule.

### Why HIGH

- **Forbidden assumption.** Attacker-selected stale signed state becomes a current trusted fact: the first TCB, including a
  known-malicious revoked binary.
- **Lower-trust inputs** (a carrier, or the submitter role) select it under an owner answer the pack presents as supported,
  below the declared root (no signing-service compromise).
- **No bound.** The stated bound is not required.
- **False statements.** The executed-equality claim and the OP-13 (c) consequences are false.

### Class and novelty

- **Narrowed remainder of BC5-1**, at its intersection with BC4-2: the first binary chosen by transport (the RV4-H2 shape) on
  a new path.
- **The instance is new.** The platform path was added in revision 6.

### Correction direction (architectural)

1. **State.** Under (c), state is always selected by a code read now from a source, or the FCM's `valid_until` is mandatory
   with a compiled maximum and refused when absent. Old packages are then bounded, and the consequence states the window.
2. **Package content.** Established first-hand before signing: the signed admitter equals a root-signed admitter digest, and
   submission is performed or authorised by the registration authority, or the package carries a root-threshold binding.
   Name the submitter in the register.
3. **Construction.** Resolve the compiled-FCM / admitter-digest construction.
4. **Instruments and tests.** Add calculator atoms `submit` and `replay`, with a revoked-binary goal. FA6's platform-only
   branch must use the package's own manifest and a submitter-signed package. Add acceptance tests for both routes.

---

## RV6-B-H3 — HIGH — No party establishes the environment manifest

**Summary.**
- Nobody establishes the manifest's recipe, component selection, upstream checksum key or supplier class.
- Whoever authors it selects the bytes of every production binary under OP-16 (a) and (b).
- OP-16 (b) counts diversity by label.
- The "pipeline selects none" claim and the OP-16 consequences are false.

### Statement

1. **The manifest.** `33` §3 fields: `components[] {name, version, sha256, upstream_url, upstream_checksum_reference,
   supplier_class}`, `assembly {recipe_digest, tool}`, `environment_tree_digest`, `supplier_class`. In the schema,
   `upstream_checksum_reference` and `tool` are free strings and `supplier_class` is one letter.
2. **What the rules establish.**
   - **R-BENV-1:** each component digest matches "a checksum signed by that component's upstream release". It checks listed
     digests, not which upstream key is trusted, which components are selected, where they are placed, or what the recipe
     adds.
   - **R-BENV-2:** environment reproducers "assemble the environment from the pinned components with the registered recipe";
     the ceremony registers when two reproductions agree. This establishes that the tree follows from the manifest, not that
     the manifest was legitimately chosen.
   - **R-BENV-5:** the quorum must span "distinct `supplier_class` values".
   - **§5:** the environment reproducer "never takes from the pipeline", yet no rule names who authors the manifest it
     assembles. `29` DR-13's selector is "environment manifests (components, recipe, tree digest, supplier class)"; the
     authority given is the two reproductions, which carry the manifest.
3. **The recurring equivalence, one level up.** *reproduced from the manifest by independent parties ⇒ manifest legitimately
   selected.* Revision 5's image record was the same selector with no authority (RV5-H2).
4. **The instruments cannot see it.**
   - CS6 G_ENV strategies are `E_pipe` (a pipeline image digest the reproductions do not match) and `E_sub` (a component
     without an upstream checksum).
   - ENV6's recipe is a digest of the component path list, and its `cer()` is given the supplier's public key by the harness.
5. **Pack statements contradicted.**
   - `33` §2 invariants (1)–(3), the §6 OP-16-ENV block, §7 "INV-ENV-PIPELINE … 0 failures" and §8 TB-S2′.
   - `21` OP-16 and §17.
   - `25` §7 row "the pipeline supplying the build image or environment record | no".
   - `30` §2 F-ENV.
   - D-0008 rules (9) ("build environments established first-hand") and (26) ("the pipeline selects none").
   - `01` G25.
   - `22` §2 BC5-2 row.

### Evidence

- **executed** `RV6-B-A02-environment-manifest-author.json`.
  - Toolchain: real `rustc 1.98.1` and system C compiler.
  - Construction: Ed25519-signed upstream SHA256SUMS; environment reproduction by fetch-by-digest and assembly; binary
    reproduction by re-assembly and a real build with the environment's `bin/cc` as linker; reviewer B r5 flags. Built after
    ENV6.

  | Scenario | Ceremony (R-BENV-1/2) | Binary reproductions | Acceptance |
  |---|---|---|---|
  | E0 control: recipe places clean components | `REGISTERED` | bit-identical `2954f713…`, "gov: genuine behaviour" | `ACCEPTED` |
  | **A07a** recipe adds inline `bin/cc` wrapper and `lib/inject.o`; every component upstream-signed and unchanged; keys pinned | `REGISTERED` | bit-identical `b9b14b2b…`, **`INJECTED-BY-ENVIRONMENT-RECIPE`** | **`ACCEPTED`** (OP-16 (a)) |
  | **A07b** placement only: the author selects the upstream's genuinely signed instrumented wrapper and runtime object | `REGISTERED` | bit-identical `c9e928a3…` (differs from E0), instrumentation runs | **`ACCEPTED`** |
  | **A07c** OP-16 (b): class-A and class-B manifests carry the same author's recipe | `REGISTERED` ×2 | injected in both classes, bit-identical | **`ACCEPTED`** |
  | control: OP-16 (b), honest recipes, class-A upstream compromised | — | differ | `REPRODUCTION_CONFLICT` |
  | **A08** two environments built only from distA (compromised), labelled A and B | `REGISTERED` ×2 | injected, bit-identical | **`ACCEPTED`** (diversity by label) |
  | A08 control: class B bound to a pinned distB key | `ENVIRONMENT_COMPONENT_UNVERIFIED` | — | — |
  | **A09** upstream key named by the manifest reference (author-generated key) | `REGISTERED` | injected | **`ACCEPTED`** |
  | A09 control: pinned upstream keys | `ENVIRONMENT_COMPONENT_UNVERIFIED` | — | — |

- **computed** same output, `computed`. CS6 is unmodified, with `releases` and `build` wrapped.
  - Strategy "pipeline-authored manifest" (components genuine, recipe common to every class): G_ENV minimal sets gain
    **{pipeline}** under OP-16 (a) and (b), for OP-9 n2q2 and n3q2. CS6's own invariants INV-ENV, INV-ENV-PIPELINE and
    INV-ONE fail. OP-16 (c) is unaffected.
  - Strategy "supplier class by label": under (b), **{env_up_a}** alone becomes minimal, and INV-ENV-B fails.
  - Control with the wrapper off: 0 invariant failures; the sets equal the committed OP-16-ENV block.
- **design** `33` §2–§8; schema; `29` DR-13; `30` §2, §4.2; `21` OP-16, §17; D-0008 (9), (26). A text search of `33` finds
  none of: the manifest author named; recipe content constrained; upstream keys pinned; supplier class established.

### Failure scenario

1. As in revision 5 with the image record, release engineering proposes the environment manifests for each release.
2. A compromised CI job adds two recipe steps: a `bin/cc` wrapper and a small object. Every component digest still matches
   its distribution's signed SHA256SUMS.
3. Both environment reproducers assemble exactly the registered recipe and agree. The custodians see upstream-verified
   components and two agreeing reproductions, and register.
4. Every binary reproducer re-assembles and builds the same injected binary, and the quorum is met.
5. Under OP-16 (b) the same author writes the class-B manifest. The injection is identical across classes, so no conflict
   arises.
6. Every machine accepts the binary.

### Why HIGH

- **TCB compromise below the declared minimum.** The bytes of every production binary are selected by an input with no
  assigned authority, the pipeline in a conforming process, under OP-16 (a) and (b).
- **False statements.** The OP-16 and D-0008 rule (26) statements are false.
- **Not CRITICAL.** OP-16 (c) holds, and a process that authors manifests outside the pipeline is possible. No rule requires
  it.

### Class and novelty

- **Narrowed remainder of BC5-2 (RV5-H2).**
- **The instance is new.** Revision 6's environment manifest moved the unestablished selector from the image digest to the
  manifest content.

### Correction direction (architectural)

1. **Manifest provenance.** The component set, placement, recipe and assembly tool are part of the registered source reviewed
   under OP-8. Alternatively, they are derived from a source lockfile by a normative assembly function with no free content.
2. **Upstream keys.** Pinned per supplier class in the root-signed Trust Policy.
3. **Supplier class.** Established from pinned key identity and disjoint component digests, never from a label.
4. **Register and calculator.** Register rows for manifest authoring and supplier-class establishment; calculator strategies
   for recipe, selection, label and upstream key.
5. **Acceptance tests.** Recipe injection; a shared recipe under (b); label diversity; a manifest-named key.

---

## MEDIUM

Each MEDIUM is carried with a bound acceptance test (`04-CARRIED-REQUIREMENTS.md`). None needs an architecture change, for the
reason given.

### RV6-B-M1 — Re-admission keeps the verifier trust store but does not apply it

- **Statement.**
  - **What is kept.** `31` R-ADM-8′ keeps anchors, clock and accepted-TBM high-waters, and per-project records at
    re-admission.
  - **What is applied.** Bootstrap-mode admission-predicate/1 takes no store input: AP-8's high-water is "running mode only".
    The genuine-binary rule (GB-1′…GB-3) reads no TBM high-water.
  - **Consequence.** After `ADMISSION_RECORD_EXPIRED` (OP-14 (b)) or `BINARY_REVOKED_SELF` (OP-15 (a)), a carrier can hand
    `gov-admit` an older genuine binary that is published and not revoked. It is admitted and runs although the store's
    accepted-TBM high-water is above its TBM.
  - **Contradicted:** `25` §7 row "a genuine older binary presented as an upgrade | no | `BINARY_T0_ROLLBACK`"; `31` §2 ("no
    admission discards the monotonic state of an earlier one" — kept, but not enforced); D-0008 rule (9) for this path.
- **Evidence.** executed `RV6-B-A04-readmission-rollback.json` (reference executor r6 unmodified; FA5 world plus R9, B9 and
  T11 built with FA5's builders):

  | Step | Result |
  |---|---|
  | first admission of B9 (TBM 2/1/10) | `ACCEPTED`; store written |
  | B9's record expired | `ADMISSION_RECORD_EXPIRED` |
  | re-admission with the current code of T11, candidate B8 (TBM 2/1/9; published, not revoked) | **`ACCEPTED`**; not first admission; store kept, `accepted_tbm.state` 10 |
  | B8 runs C2 | **`ALLOWED`** |
  | running mode, same shape (committed P4r5 and P4r6 row `RV3-D-A13r5_older_binary_after_newer`) | `BINARY_T0_ROLLBACK` |

  Code: `accept` has no store parameter; neither `accept` nor `gov_run` reads `accepted_tbm`. RT-170 tests only E10
  downgrade.
- **Failure scenario.**
  1. A workstation under OP-14 (b) re-admits after expiry.
  2. A proxy serves the older 4.1.7 `gov`, genuine and still published.
  3. The machine now enforces 4.1.7's compiled floors and Trust Policy identity, older than what it had accepted.
- **Why MEDIUM, carriable.** The binary is genuine, published and unrevoked, and the owner's `min_binary_version` bounds it.
  The trigger needs an operator re-admission plus a carrier. A bound rule and a test close it with no new trust relationship.
- **Correction.** At re-admission, bootstrap mode applies the store's accepted-TBM high-water and refuses an FCM epoch below the
  store's anchors. Alternatively, GB rules refuse above C0 a running binary whose TBM is below the store's high-water.

### RV6-B-M2 — Generated CONTENT statements print the repository-writer atom as "1 reproducer key"

- **Statement.**
  - **The rendering.** `CS6.compact()` counts atoms starting with `rep` as reproducer keys, so `repo` (A2, the repository
    writer) renders as "1 reproducer key".
  - **Where it appears.** Every G_CONTENT minimal set containing `repo` is affected: 120 sets over 96 configurations. No
    G_CONTENT configuration has a reproducer atom, because `atoms_for` excludes them. The generated CONTENT block in `21` and
    `34` prints "reproducer key" in 8 of its 24 rows, all USE rows.
  - **Why the check passes.** `statements_check.py` S1 compares the rendering with itself and passes. S2 rejects the same text
    when it is hand-written outside a block, and accepts the true form "{…, repo, …}".
  - **Effect.** The owner reads that effective content on a Git-delivered release (USE) needs a reproducer key, where it needs
    repository write.
- **Evidence.** computed and executed `RV6-B-A03-generated-statement-rendering.json` (CS6 module and `statements_check.py` on a
  scratch copy of the pack).
- **Why MEDIUM, carriable.** The false consequence statements belong to security-material options (OP-2, OP-4, OP-8): the BC5-4
  class. The sets are correct in the calculator. A rendering fix, plus an atom-level comparison in S1, is a bound deliverable.

### RV6-B-M3 — Register completeness is checked over rule ids, not over selectors

- **Statement.** `register_check.py` C2 requires every rule id of the scoped rule tables to belong to a decision.
  - Selectors that no rule names escape it: first-contact value composition (H1); platform package submission and package FCM
    currency (H2); environment manifest authoring and supplier-class establishment (H3).
  - DR-06 and DR-13 name these values, but assign their authority to parties that carry them.
  - CS6's strategies derive from the register, so the calculator cannot see these selectors, and RT-128/RT-183 pass.
- **Evidence.** computed: REGISTER-CHECK re-run PASS (byte-identical); adding the strategies makes CS6's own invariants fail
  (A01 part C; A02 `computed`).
- **Why MEDIUM.** The defects it hides are H1–H3, counted there. The mechanism is carriable: completeness is extended to every
  statement or schema field that selects a value of a decision, and each such field must name its establishing party.

## LOW

| ID | Statement | Evidence | Carried as |
|---|---|---|---|
| **RV6-B-L1** | **R-CON-5 lists only name-matched security units.** `csi_lib.SECURITY_CLASSIFIED_NAMES` and prefixes omit `commands/`, `overlay-templates/`, `taxonomy/` and `KERNEL.yaml`. A registration change to `COMMAND_CONTRACT.yaml` (4.1.5 intent routing, adapters, audit), to `overlay-templates/TOOL_PERMISSIONS.yaml` (seeds a new project's tool permissions at `init`), or to taxonomy is not listed in the per-project `registration_change` gate. Selection is unaffected: `verify-registration` refuses each non-first-hand proposal. | executed `RV6-B-A10-surface-classes.json`: `registration-changes` exit 0 for K1–K3 and 8 for the SECURITY_POLICY control; `verify-registration` exit 3 for every changed proposal against the custodian's K0 build; code lines in 4.1.5 runtime | CR6-B-04 |
| **RV6-B-L2** | **Stale revision-5 text.** `05` §2's compiled statement-type table lists `release-registration.v1`, `binary-reproduction.v1`, `verification-attestation.v3` and `input-manifest.v1`; §1 and the schemas define v2, v2, v4 and v2. `05` §1's `trust-state` row says "First admission: never selected unless its fingerprint is typed". | design | CR6-B-05 |
| **RV6-B-L3** | **Verification precedes environment registration.** R-VER-1 has the verifier reproduce "in a registered environment", but `06` §2 step 4 orders verification (3) before environment reproductions (5) and registration (6). The verifier's environment at verification time has no stated source. It is the same unestablished manifest as H3. | design | CR6-B-06 |
| **RV6-B-L4** | **Derivation-tool provenance at the ceremony is unstated.** R-CON-1 has each custodian run `gov release build --kernel-only` and `csi_check.py verify-registration` on its own build. No rule states which binary and script: an admitted `gov` and a checker from the registered source, never a pipeline-supplied tool. | design | CR6-B-07 |

## INFO

| ID | Statement |
|---|---|
| RV6-B-I1 | RV5-I1 is unchanged: the acting role remains caller-declared, and no trust gate depends on it (`27` §5). |
