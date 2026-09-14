# 02 — Held-out attack register RV7-B-A01 … A13 (review r7 B, AR-0020)

This review authored these attacks. None of them is an acceptance case of `12-ACCEPTANCE-TEST-PLAN.md` (RT-184…RT-202 and the
extended rows), an architect self-attack (`28` A-R7-01…A-R7-15), or an attack of reviews r2–r6. Each row names the nearest
existing case and says why it does not cover the attack.

## Evidence classes

| Class | Meaning |
|---|---|
| **E** | Executed: the reference executor `evidence/r7/gov_admit_reference_r7.py` (unmodified, via `w7world.py`; real Ed25519 through OpenSSL; `sha256sum`), or an architect instrument run unmodified |
| **C** | Computed: CS7 loaded unmodified, functions wrapped, originals called, control equal to the committed blocks; or BA11r7's source re-evaluated with one stated assumption replaced |
| **D** | Design or code reading at `d07d200` |

## Register

| ID | Attack | Adversary | Expected secure outcome | Revision 7 as written | Class, evidence | Nearest case (why not covered) | Finding |
|---|---|---|---|---|---|---|---|
| **RV7-B-A01** | **Revocation omission.** The revocation authority revokes R9 (2 of 3, issued 102 h before admission). Daily Trust States signed by two trust-state keys keep R9 published and never list the revocation (an omission, not a drop). The statement is in the bundle. Victims: first install, ten later days, re-admission over a store that predates the revocation. | trust-state publication process (as written); or the trust-state threshold with it | Refused; or bounded by a stated, tested listing delay | Custodians publish every state. `ACCEPTED` on all 11 daily states (revocation up to 342 h old), and on re-admission over the older store. Controls: a listed revocation, a store holding the negative, and a drop all refuse. | E: `outputs/RV7-B-A01.json`; C: `outputs/RV7-B-CS7.json` A01-VA `{fcpub}`, A01-VB `{2 trust-state keys, fcpub}` for FA and RA_unheld; P2 with `transport` | A-R7-02 and RT-184 (a *drop* of a published revocation); A-R7-05, CUR7 W and RT-191 (a revocation 6 h old, inside the window) | **H1** |
| **RV7-B-A02** | **Stale state at C3.** (a) A workstation anchored at T5, with T9 (revoking R7) withheld; the operator types stored T7 codes (4 months old) into a C3 gate. (b) A CI image admitted 6 days ago; provisioning re-stamps the pin's `provisioned_at` and keeps the image-build state code. (c) BA11r7 with typed codes naming the effective state instead of an assumed `sources_latest`. | stored or replayed codes (runbook, pin template, cached page) with transport withholding | `TRUST_STATE_CURRENCY_UNPROVEN`, as FC-9 refuses the same codes at admission | (a) C3 `ALLOWED`, while `gov-admit` gives `FIRST_CONTACT_STATE_TOO_OLD` for the same codes; (b) C3 `ALLOWED` (control as provisioned: refused); (c) `no_C3_on_a_state_below_t9` flips to false | E + C: `outputs/RV7-B-A02.json`; C: `outputs/RV7-B-CS7.json` A02 `{transport, stored_old}` for P2, removed by A02-FIX | A-R7-08 (claims no C3; its evidence BA11r7 hard-codes that typed codes equal what the sources publish); RT-101 (c) (in-gate code of the effective state proceeds: the attack's precondition); RT-147 (thief descendant) | **H2** |
| **RV7-B-A03** | **One onboarding record designates both sources.** The organisation's copy of the root ceremony record (R-FCD-2) is altered to name two look-alike sources that serve a self-consistent FCA, state code, procedure digest and substituted admitter. | editor of the onboarding copy; no source, custodian or key | Two independent designation inputs required, or a stated one-input root set | Calculator: `{onboard}` is minimal for FA (G_BYTES and G_REVOKED); the committed root lists pairs only. Executed row FA7 S2 D: `ACCEPTED_BY_SUBSTITUTED_EVALUATOR`. | C: `outputs/RV7-B-CS7.json` A03; E: FA7 S2 D (re-run byte-identical) | FA7 S2 D and RT-184 (both look-alike pages as two atoms); PI-01 and DR-38 (one record, not modelled as one atom) | **M1** |
| **RV7-B-A04** | **Same upstream under other spellings.** Registry entry `sup-A2` names Debian images, the archive, buildd and the keyring under different strings, with a second key of the same upstream; reproductions in `sup-A` and `sup-A2`. | registry proposal accepted at root threshold (hidden common provenance) | Not counted as two independent classes | `independent_classes` = 2; `ACCEPTED`. Controls: identical strings and a shared key → `ENVIRONMENT_DIVERSITY_NOT_MET`. | E: `outputs/RV7-B-A04-A05.json` A04 | ENV7 A08, FA7 R8, RT-186 (identical provenance strings) | **L1** |
| **RV7-B-A05** | **Root-held purposes below root threshold in the schema.** A root granting `trust-policy` and `first-contact-authority` at threshold 1 to a non-root key, validated against `trust-root.schema.json`. | a draft or implementation relying on schema validation | Schema refuses as the compiled check does | Schema: 0 errors. Compiled `root_conforms`: refused (`threshold(trust-policy)`). | E: `outputs/RV7-B-A04-A05.json` A05 | PROF7 EX-09 and EX-10 (registration and final shapes, not these two purposes); FA7 S2 P (FCA by one root key, a signature case) | **L2** |
| **RV7-B-A06** | **Is A01 only an executor defect?** A scratch mutant of the executor applies every verified revocation statement held; A01's state is presented with the statement delivered, then withheld by transport. | as A01, plus transport | Refused in both | Delivered: `BINARY_REVOKED`. Withheld: `ACCEPTED`. | E: `outputs/RV7-B-A01m.json` | none | supports **H1** (an architectural correction is needed) |
| **RV7-B-A07** | **Source custodian without history.** `custodian_publish` for a custodian that has published nothing (new or rotated source) given T11d, which drops the published R7 revocations. | two trust-state keys plus a rotation of both sources | Refused (`STATE_DROPS_REVOCATIONS`) | Published. With one source rotated, the other refuses (fail closed). | E: `outputs/RV7-B-A01.json` publication row | FA7 S2 P `two_trust_state_keys_descendant_drops_revocation` (custodian with history) | **L3** |
| **RV7-B-A08** | **PROF7 mutation sensitivity.** The architect's PROF7, unmodified, on a scratch export in which `trust-root` purposes gain `freshness-witness` and the `trust-policy` bootstrap gains `channel_quorum`. | — (instrument honesty) | EX-01 and EX-04 fail; nothing else changes | EX-01 and EX-04 fail on exactly those schema checks; every other exclusion holds | E: `outputs/RV7-B-A08-PROF7-mutation-sensitivity.json` | A-R7-13 (PROF7 on the committed pack) | none (holds) |
| **RV7-B-A09** | **Exclusion reachability sweep** over the 28 certified schemas: excluded-mode identifiers outside descriptions, objects with properties that allow additional properties, external `$ref` to withdrawn schemas. | — | No excluded mode can validate | Identifiers only in descriptions, except the `freshness` verdict axis of the framework lock (not a witness mode). No external `$ref`. The one open object is `trust-policy.surface` (validated by the CSI schema). | E: `outputs/RV7-B-A09.json` | PROF7 schema checks (named pointers only) | none (holds; see A05) |
| **RV7-B-A10** | **Issuance cadence.** What must hold for any first admission to succeed on a given day, and where is it stated? | — (availability of a security control) | A stated trust-state and publication cadence of at most 24 hours | Not stated; OT-1a mentions daily re-issuance only for media | D: text search | CUR7 A08 (age refusal), OT-1 (media only) | **L4** |
| **RV7-B-A11** | **Re-run fidelity of committed evidence.** The architect's runner re-run from a scratch export; 68 outputs compared. | — (evidence honesty) | Byte-identical except declared run-dependent leaves | 53 identical; 8 run-dependent; 2 stale committed outputs (no verdict leaf); 5 not runnable, as disclosed; the runner cascades on the reviewer-C input and the examples path | E: `rerun/COMPARISON.json`, logs | `22` §1, §12 (determinism passes on the architect's own tree) | **L5** |
| **RV7-B-A12** | **OP-8 independence mechanics.** Can one verifier holding both `verification-attestation` keys satisfy AP-5 with two self-assigned execution ids and report digests? | one verifier with two keys | Two genuinely separate verifiers required | AP-5 checks distinct key ids, execution ids and report digests only; custody rests on TA-11 and R-REG-3 (d) | D + code: `accept` AP-5 loop | PROF7 EX-13 and FA7 R6 (same execution id or same report digest) | **I1** |
| **RV7-B-A13** | **Genesis of the custodians' verifier.** At lineage genesis, with no codes yet published, which binary verifies the first FCA and Trust State for R-FCS-1 ("its own admitted binary")? | whoever supplies that binary (pipeline, carrier) | A stated genesis procedure at the registration or root authority | Not stated; admission needs both sources' codes, which need the custodians' verification | D: text search | R-BENV-9 (derivation tools, not the custodian verifier); RT-180 (custody, not tooling) | **L6** |

## Re-execution of prior probes and the architect's instruments

Logs: `evidence/rerun/architect-runner-log.tsv` and `evidence/rerun/dependent-rerun-log.tsv`. Comparison:
`evidence/rerun/COMPARISON.json`. Every run used a scratch export of `d07d200` (identical to the review base for the pack, `spec/`
and `docs/`).

| Probe (origin) | How re-executed | Revision 7 result | Status of the architect's claim |
|---|---|---|---|
| CS7, FA7 ×2, CUR7, ADM7, ENV7 (real `rustc 1.98.1`), BA11r7, BA12r7, PPR7, DA05r7, DA06r7, PROF7, STATEMENTS-CHECK (architect) | committed runner, adapted | byte-identical; `CS7-results.json.gz` uncompressed byte-identical | reproduced. Model gaps: CS7 has no omission strategy (A01) and no stored-code C3 victim (A02); BA11r7's C3 rows rest on `sources_latest` (A02); designation atoms (A03). |
| REGISTER-CHECK, DA09r7, DA04r7, EXAMPLES (architect) | re-run after the cascade, with the committed `crashmig7.json` as input; EXAMPLES in place | byte-identical to the logged digests | reproduced (runner defect L5); register C9–C11 pass, but the establishing party of listing completeness is absent (H1) |
| PROF7 mutation (this review) | A08 | EX-01 and EX-04 detected | instrument load-bearing |
| CSI self-test (78/78) and checks; P4r6; CS6; DA03r6; FA6; CON6; SRC6; UW6; ATTR6; ENV6; P4r5; DA03r5; FA5; REG5; P1r4; CS5 (retained) | runner | byte-identical, except CSI `kernel_dir` ×5 and ADM6 race counts (run-dependent) | retained closures reproduced |
| DA07r6 on the revision-7 plan (retained) | runner | 2 leaves differ (RT-201 now in the plan); verdict leaves equal | committed output stale (L5) |
| RV6-B-A01 (parts P, S, C, R), RV6-B-A02 (A07a/b/c, A08, A09) | unmodified: cannot run (withdrawn schema, withdrawn field), confirming `NOT-RUNNABLE.json`. Re-expressions FA7 S2 P/D/X and S3, CUR7 R, ENV7 re-run byte-identical and read. | composer, submitter, printer, replay and manifest-author instances refused | **closed as instances**; class remainders A01 (H1), A03 (M1) |
| RV6-B-A03 | unmodified | S2 now rejects the misrendered set; 2 `sets_checked` leaves differ from the committed re-run output | closed (RV6-M1); committed output stale (L5) |
| RV6-B-A04 | unmodified (revision-6 executor) byte-identical to the committed re-run; CUR7 A04 | `BINARY_T0_ROLLBACK` at re-admission and at use | closed (RV6-L5) |
| RV6-B-A05, A06 | within A01 R and S (unrunnable); CUR7 R; PROF7 EX-04 and EX-05 | `FIRST_CONTACT_STATE_TOO_OLD`; `PROFILE_MODE_EXCLUDED` | closed |
| RV6-B-A07, A08, A09 | within A02 (unrunnable); ENV7 | `ENVIRONMENT_MANIFEST_NOT_DERIVED`, `…_DIVERSITY_NOT_MET`, `…_COMPONENT_UNVERIFIED` | closed; label remainder at root threshold (L1) |
| RV6-B-A10 | unmodified byte-identical | default deny holds; unlisted security-relevant changes still not listed without a flag | RV6-L1 open (carried, RT-198) |
| RV6-B-A11 | unmodified byte-identical (revision-6 model); BA11r7 re-run | 0 `current`; C3 rows as the model assumes | holds within the model; the assumption is false (A02 → H2) |
| RV6-B-A12 | unmodified byte-identical (revision-6 model); BA12r7 re-run | 0 accepts with ≤ 1 key | holds |
| RV6-B-A13 (anchors from a composed value) | design; A02 | state codes come from both sources, but a stored code is accepted at C3 | narrowed → H2 |
| RV6-B-A14, A15 | design | R-BENV-8 and R-BENV-9 specified; RT-200 and RT-186 | closed in specification; custodian-verifier genesis open (A13 → L6) |
| RV6-B-A16 | REGISTER-CHECK C9–C11, DA09r7 (578 fields) re-run | 0 unregistered inputs by the check's definition | narrowed: listing completeness has no establishing party (H1) |
| RV6-D-A01 | unmodified byte-identical; FA7 S2 D | attacker lineage refused; substituted evaluator only with both look-alike pages | closed as stated; designation as one input → M1 |
| RV6-D-A02 | unmodified byte-identical; CUR7 A02 | `READMISSION_STATE_BELOW_HELD`, `BINARY_REVOKED_IN_HELD_STATE` | closed |
| RV6-D-A03 | unmodified byte-identical | default deny; first-hand refusal (exit 3) | holds; RV6-L1 carried |
| RV6-D-A04 | unmodified byte-identical; DA04r7 15/15 | detected | closed |
| RV6-D-A05, A08, A09 | unmodified: cannot run (confirmed); DA05r7, CUR7 A08, DA09r7 byte-identical | as architect | closed as instances |
| RV6-D-A06 | unmodified byte-identical; DA06r7 | injective renderer | closed |
| RV6-D-A07 | unmodified byte-identical; ADM7 A07 | protected store decides first admission | closed (RV6-M6 trust part) |
| RV5-B-A01, A04, A09, A12; RV5-D-A01, A03, A04, A05, A07 | unmodified | byte-identical | retained |
| RV5-B-A05, A08 | unmodified | run-dependent leaves only (archive and image digests) | retained |

## Counts

| Item | Count |
|---|---|
| Held-out attacks authored | **13** (A01–A13) |
| Executed (primary) | 9 (A01, A02, A04, A05, A06, A07, A08, A09, A11) |
| Computed parts | 3 (A01, A02, A03) |
| Design | 2 (A10, A13), plus A12 as design and code |
| Contradicting a stated pack or evidence claim | 5 (A01: CUR-R1 and CP-REVOKED; A02: `24` §6, RS-1b and A-R7-08; A03: CP-FC-ROOT and FC-R1′; A04: `33` §2 (4) "never from labels"; A11: committed outputs versus re-run) |
| Exposing an unstated rule (gap) | 4 (A05, A07, A10, A13) |
| Leading to HIGH | A01 (with A06) → H1; A02 → H2 |
| Leading to MEDIUM | A03 → M1 |
| Leading to LOW | A04 → L1; A05 → L2; A07 → L3; A10 → L4; A11 → L5; A13 → L6 |
| Leading to INFO | A12 → I1 |
| Holding (no finding) | A08, A09 |
