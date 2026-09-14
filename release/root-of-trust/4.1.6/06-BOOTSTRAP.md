# Output 6 — Bootstrap model

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 5 changes (BC4-1, BC4-2):
> - releases are **registered** once per release and binaries are **reproduced by a first-person quorum** (`30`);
> - the first binary on every machine, every CI image and every legacy consumer's first RoT-1 binary are admitted by the
>   **independent executor `gov-admit`** with a fingerprint typed now; the candidate is never executed and the measured
>   bytes are installed (`31`);
> - no trust ceremony runs on a binary that has not been admitted (`31` GB-1, R-CER-1);
> - revision 4's first-binary paths (b) "independent tooling verifying A2–A6" and (c) "build and compare `gov version
>   --trust`" are **withdrawn** (RV4-H2).

## 1. The problem

Every downloaded artefact can be replaced together with anything that claims to authenticate it. Trust enters once, by a
value published independently of the download channel and typed by a person now; it is carried forward by signatures and
first-hand establishment. Two such values exist: the **trust-root id** (lineage) and the **state fingerprint** of every
Trust State Statement (`24` §3.1), which commits to the lineage, root, Trust Policy and Trust State. A third published value,
the **admitter digest**, lets the operator select the executor that evaluates the first binary.

## 2. Production bootstrap

1. **Root ceremony** (once per lineage). Root keys offline; root v1 with grants that satisfy the whitelist and the Fact
   Threshold Check (`05` §3), including the reproducer quorum and the registration authority of OP-2.
2. **Independent channels.** At least two channels that do not share an attacker with the release host publish the root
   fingerprint once per lineage, the state fingerprint of every new TSS and the admitter digest. Qualifying channels: an
   offline ceremony record; owner infrastructure that is not the Git host and does not deploy from it; direct authenticated
   communication. Repository copies are convenience copies.
3. **Constitution.** `gov trust draft-policy` produces the Trust Policy draft (classification, floors, precedence, Overlay
   Surface, owner-domain slots and binding groups, eligibility, bootstrap and registration parameters, lowering history) and
   runs the derivation calculator (`29` §5.3). The root ceremony reviews and signs.
4. **Release.** Reproducible payload build with `release.source {release_commit, content_digest}` and the input manifest →
   `release-candidate` signature → independent verification records returned first-hand (OP-8) → promotion
   (`release-final`, V8) → **registration** (`30` §5, R-REG-3 checks) → certification (optional).
5. **Binaries.** Every registered target is built reproducibly by n independent reproducers from the registered source and
   the manifest inputs fetched by digest; each signs a one-signature reproduction and confirms first-hand to the publisher
   (`30` §7). The publisher references the registration and exactly one quorum-reproduced digest per target in the next TSS
   and publishes its fingerprint (`30` §8). The admitter is registered and reproduced the same way.
6. **First binary on a machine: independent admission only** (`31` §4). Download `gov-admit` and compare its digest with
   the channels; type the current state fingerprint (OP-13); `gov-admit` evaluates admission-predicate/1 (`25` §5) over the
   bytes it read, installs from its buffer and writes the admission record. There is no other first-binary path.
7. **Subsequent binaries** are accepted by the admitted `gov` running the same predicate with its anchors and a currency
   proof that names the TSS publishing the binary (`25` AP-3).

## 3. First-install ceremony on a machine

| Step | Command | Runs on | Establishes |
|---|---|---|---|
| 0 | compare the `gov-admit` digest with the channels (platform hash tool) | the operator's platform tools | admitter selection (TA-5) |
| 1 | `gov-admit --fingerprint <typed> [--fingerprint <typed from second channel>] --statements <bundle> --install <dest> <candidate>` | `gov-admit` | TCB admission; lineage confirmation (the fingerprint commits to it); fresh verifier trust store (`31` R-ADM-8) |
| 2 | `gov trust confirm-state <fingerprint>` typed again, or a protected pin | the **admitted** `gov` | anchor, satisfied by inclusion (`24` §3.2, §3.4) |
| 3 | `gov trust refresh --from <bundle>` if the machine is `BELOW_ANCHOR` | the admitted `gov` | knowledge at the anchored epoch |
| 4 | `gov init` / `gov update --apply`, with the local trust gate (`27`) and a currency proof naming the TSS used | the admitted `gov` | installation |

Before step 1 completes, every RoT-1 `gov` on the machine runs C0 only (`31` GB-1).

**Automation.** Pins and decision pins live in the system pin directory, or in the account configuration only where the
integrity predicate holds; they are provisioned outside the repository writer's control (TA-9, `24` §3.5). A **CI runner
image** runs step 1 at image build with the operator-provisioned fingerprint, writes a root-owned admission record with
`valid_until` ≤ `pin_max_validity_days` beside a root-owned state pin naming the same TSS, and runs jobs as another user.
Images are rebuilt before either expires (`31` §7). A job with passwordless `sudo` can write `/etc/gov` and violates TA-9
(CR4-B-01 (d)).

No environment variable, flag or repository file can confirm a lineage, anchor a state or admit a binary (D-0008 rule 15).

## 4. Lineage pinning and mismatch

Unchanged: the verifier trust store pins the lineage; the lock records `trust_root.id`; a binary whose compiled lineage
differs is `TRUST_ROOT_LINEAGE_MISMATCH`; re-rooting after a threshold compromise needs `gov trust adopt-lineage` by a human
through the `adopt_lineage` trust gate, and re-admission of the binary under the new lineage.

## 5. Consumer repository on a new machine

A clone carries `governance/trust/**` (kernel, release and registration statements, state, root links, FORMAT, lock) and the
occupation entries (`26` §2). The admitted binary authenticates them offline. The new machine's verifier trust store starts
empty (fresh at admission): it is `UNANCHORED` until step 2; what it may do meanwhile is OP-7 (`24` §4.3); trust ingress is
refused.

## 6. Development builds

`cargo build` from a checkout compiles that checkout's trust data into a TBM marked `build: development`. Such a binary is
never admitted, never records an accepted TBM, and never produces production eligibility for unregistered material.

## 7. Test fixtures

`gov-test-profile` compiles the test lineage with the twelve purposes of revision 5.

## 8. Classification summary

| Class | Selected by | Authenticity / stage | Production eligibility | Doctor |
|---|---|---|---|---|
| Production final, registered | registration (OP-2) referenced by the effective TSS | `AUTHENTICATED` / `final` | per `19` §6 (E7 with the release's registration) | clean |
| Production final, not registered (or not yet held) | — | `AUTHENTICATED` / `final` | ineligible (`release_unregistered`) | HIGH |
| Production candidate | `release-candidate` | `AUTHENTICATED` / `candidate` | `ELIGIBLE_EVALUATION` only | HIGH |
| Legacy 4.1.2–4.1.5 | TPS `eligibility.historical_releases` (root threshold) | `HISTORICAL_IDENTIFIED` | never | CRITICAL when installed |
| Development unsigned | nobody | `DEVELOPMENT_UNSIGNED` | never | HIGH |
| Production binary | admission-predicate/1: registration + reproduction quorum + publication + negatives + currency, by an evaluator other than the candidate | admitted, record written | TBM ≥ accepted-TBM high-water | — |
