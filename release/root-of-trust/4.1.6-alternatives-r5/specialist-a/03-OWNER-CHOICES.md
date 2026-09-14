# 03 — Genuine owner trade-offs under the Selection-Authority Model (specialist A)

> **Nothing here is decided, and no default is proposed.** Each choice below is one that only the owner can make: every
> option satisfies SEL-1 and HO-0001 §3, and the options differ in security margin, availability or operating cost.
> Consequences are computed or read from `01-ALTERNATIVE.md` and the evidence cited.

## Not owner choices under SAM (architecture minima)

These are not offered as options, because every alternative re-creates a selector below the authority it confers
(`00-ROOT-CAUSE.md` §5):
- SEL-1 and the compiled selector register;
- exact per-release registration of non-orderable units (ranges fail E4);
- reversion as a computed reduction, and append-only registrations;
- a reproduction quorum of at least 2 first-person reproductions, with conflict refusal;
- build inputs fetched by digest;
- reproductions submitted outside the pipeline (E2: {pipeline, 2 keys} otherwise);
- first acceptance selected by a typed fingerprint and executed by an independent executor that never runs the candidate;
- no TA-5 ceremony before acceptance;
- KS-7 and KS-12.

**Revision-4 options removed by SAM:**
- OP-2 source authority S0–S3 and `release-artifact` (i)–(iii): source is always selected at registration;
- OP-4 as a production security option;
- OP-6 (b) (trust on first use) for production.

**Retained unchanged:** OP-1 (root keys, threshold, custodians), OP-3, OP-5.

## OC-1 — Who registers each release

**The question.** Which authority selects source, build inputs and non-orderable constitutional content for every release?

| Option | What it means | Minimum to register a malicious release (E2) | Consequences |
|---|---|---|---|
| (a) **root threshold** | every release registration is in a root-signed Trust Policy | 2 of the 3 root keys (A8 class: root compromise) | **Strongest custody.** Root keys are used once per release, not once per kernel change. A security fix waits for a root ceremony. Root custodians must perform the R-REG-3 input-manifest check themselves. |
| (b) **delegated `release-registration` quorum** | root grants a separate purpose; compiled threshold ≥ 2; keys shared with no other purpose; root rotates it | 2 delegated keys | **Root stays offline between rotations.** The delegated quorum becomes the target that selects source, inputs and non-orderable content for new releases. Floors and registered precedence (root) still bound the content. A compromise is remedied by root rotation plus revocation of the registrations it made. |

**Both options** need a trust-state reference and reproductions for binaries to be accepted (E2 minimal sets). Neither option
changes the verifier.

## OC-2 — Reproducer count and quorum

| Option | Consequences |
|---|---|
| (a) n = 2, q = 2 | **Availability.** One reproducer unavailable blocks a binary release. **Denial of service.** One stolen key blocks a release through a conflict (AV-S1). **Minimum for malicious bytes:** both keys, plus trust-state key and transport on P1 machines (E2). |
| (b) n = 3, q = 2 | **Availability.** Tolerates one unavailable reproducer. **Denial of service:** unchanged. **Minimum:** any 2 of 3 keys plus the same (E2). **Cost:** a third independent environment and custodian. |
| (c) n = 3, q = 3 | **Minimum:** all 3 keys for malicious bytes. **Availability:** any one unavailable blocks a release. |

**Independence requirements across reproducers** (different organisations, hosting providers or build-image lineages) are
part of this choice. They are assumptions (TA-10′), not verifier checks.

## OC-3 — Common-mode toolchain (TA-12)

**The problem.** A compromised upstream toolchain release that passes the ceremony's signature check makes every honest
reproducer produce the same malicious bytes, with zero keys (E2 `toolchain_upstream`).

| Option | Consequences |
|---|---|
| (a) accept TA-12 | no added cost. **Residual:** the upstream toolchain publisher's release process is in the TCB. |
| (b) diverse toolchain reproduction: at least one reproducer builds with an independently bootstrapped compiler (for example diverse double-compiling) and must obtain the identical digest | removes the single upstream as a selector. High engineering and build-time cost; reproducibility across toolchains may require restrictions on compiler features. |
| (c) owner-built toolchain archive registered as an input | moves the toolchain selector to the owner's own build of the compiler, which then needs its own reproduction. Cost between (a) and (b). |

## OC-4 — Integrity of the installed binary for trust ingress

**The problem.** Acceptance binds a digest; a same-uid process can replace a binary installed where the account can write
(E3 N-FB8).

| Option | Consequences |
|---|---|
| (a) C3 (trust ingress, including binary upgrade) only from a **protected install location** (the file and every ancestor owned by another uid and not writable by the effective uid) | closes VR-B1. Needs a privileged install (`sudo`, a system package location, or an administrator on Windows). Developer installs in `~/.local/bin` get C0–C2 only. CI images install as root and run jobs as another user (already required by TA-9). |
| (b) any location; residual VR-B1 stated | no privileged install. An A3 process (a planted hook or a malicious dependency run by the user) can replace the TCB between runs; that is the same class as RS-3 and RV4-M2, now reaching the binary itself. |
| (c) any location, but each C3 re-measures the running executable with `gov-accept` against the `accepted_binaries[]` record | detects replacement only if `gov-accept` itself and its record are not replaced. Both are same-uid writable in a user install, so this reduces to (b) against A3. It adds a step to every C3. |

## OC-5 — Retention of releases whose non-orderable content was superseded

**The problem.** SAM guarantees that later releases cannot carry superseded content. It does not by itself decide whether
older releases remain eligible at their own registration. On machines without a per-project record, the repository writer
selects among eligible releases (RR-2).

| Option | Consequences |
|---|---|
| (a) keep older releases eligible | installed projects keep working. A repository writer can deliver an older eligible release, with its older non-orderable content, to fresh clones and CI runners (RR-2, retained). Machines with a record refuse the downgrade (E10). |
| (b) on every **security-relevant** content change, raise `min_release_sequence` in the same ceremony | older releases become ineligible everywhere the Trust Policy reaches. Installed projects fall back to the EmbeddedSnapshot of the running binary, or refuse at decision points, until they update. Classifying a change as security-relevant is a ceremony judgement. |
| (c) retirement with a grace period (`eligible_until` on the older registration) | as (b) after the date; as (a) before it. Adds TA-7 (clock) to eligibility, a new clock dependency. |

## OC-6 — What a genuine but revoked running binary may still do (self-restriction, R-SUB-2)

| Option | Consequences |
|---|---|
| (a) C0 only | strongest. Incident response on the machine needs a new binary obtained through `gov-accept` first. |
| (b) C0–C2; C3 refused | allows governed work to continue while a replacement is obtained. A binary revoked for a defect in C1–C2 enforcement keeps enforcing with that defect until replaced. |

## OC-7 — Currency for machines without a current proof (revision 4 OP-7, restated under SAM)

The options and parameters are those of revision 4 `24` §9 and `21` OP-7. SAM changes three consequence statements:
- **Independence from OP-7.** First binary acceptance does not depend on OP-7 (typed fingerprint, no clock).
- **RS-2 restated.** Under (a), (b), (d) and on stateless runners there is no clock-rollback detection (CR4-B-03).
- **Witness input.** Under (c) the witness service's input is a registered selector (owner ceremony or channel, CR4-B-02).
  Custody of two witness keys in one service remains the one-custody consequence unless separated.

| Option | Genuine trade-off retained |
|---|---|
| (a) anchored only | C1–C2 at any age of a human or retained anchor; C3 needs a proof; CI pins re-provisioned per window |
| (b) maximum anchor age | bounds the C1–C2 exposure on every machine; needs an honest clock and periodic re-confirmation |
| (c) expiring witnesses | stateless runners without pins; adds witness custody and TA-7; witness-key compromise exposure |
| (d) compiled epoch for use | C1–C2 on unanchored machines at any genuine state ≥ the compiled TSS, indefinitely, labelled; never C3 |

## OC-8 — How the independent executor reaches first machines

| Option | Consequences |
|---|---|
| (a) owner-published `gov-accept` whose digest is in the independent channels | TCB on the first machine is the owner's executor, the platform interpreter and OpenSSL (TA-1b). The operator compares a digest (TA-5). |
| (b) `gov-accept` distributed through OS package managers | easier installation. **Adds the distribution's signing keys and build infrastructure to the first machine's TCB**, which the owner does not control. |
| (c) a documented manual procedure with platform tools only (OpenSSL, `sha256sum`, a JSON canonicaliser) | no owner program in the TCB. Error-prone; the procedure itself must be followed exactly (A10 social engineering). Conformance cannot be tested on the operator's machine. |
