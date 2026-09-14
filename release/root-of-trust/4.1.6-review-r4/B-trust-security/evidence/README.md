# Evidence — review r4 B (trust and security), run AR-0006

**Scratch only.**
- **Repository.** The worktree is read and never written, except this output directory.
- **Probe scratch.** Probes ran under `…/scratchpad/ar-0006/` with `env -i`, so no `GOV_*` variables reached any child.
  `HOME` and `GOV_KERNEL_CACHE` pointed into scratch, and `PYTHONDONTWRITEBYTECODE=1` was set.
- **Account home.** The account's real home is never written.
- **Legacy binaries.** Used read-only; SHA-256 in `ARCH-RERUN-LOG.json`.
- **Placeholders.** In committed outputs, absolute paths are replaced by `<scratch>`, `<worktree>`, `<legacy-bin>` and
  `<scratchpad>`.
- **No RoT-1 binary exists.** Revision-4 behaviour is established with:
  - the pack's own checker;
  - the architect's P4r4 functions, loaded unmodified;
  - an independent reference model written from the text;
  - the real 4.1.5 binary as a stand-in consumer or command runner.

## Files

| File | Kind | What it establishes | Result |
|---|---|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | record | SHA-256 and Git blob id of every reviewed file at `bca05a7`: the pack, D-0007, D-0008, ARCH-0002, `docs/DECISIONS.md`, and review r3 files. Identical at base `7a23900`. | 227 files |
| `ARCH-RERUN-LOG.json` | record | Re-execution of the architect's instruments | selftest 56/56; checker exits 0/3/2/2/2; P4r4, VA4, P1r4 byte-identical |
| `RV4-B-M-reference-model.{py,json,stderr}` | computed (independent) | **R** review r3 constructions under revision 4. **MX** 336-row matrix (12 machine variants × OP-7 × 7 adversaries). **PS** parameter sweep. **BC** binary acceptance by every capability subset with honest custodians. **FB** first binary. **AT** accepted-TBM. **LB** labels and decision rule. | R 18/18 hold. MX 0 unstated, 0 `current`. BC: malicious bytes 1 key + pipeline under every OP-2/OP-4; malicious source 1 key + pipeline under (S0)/(S3). FB: tooling A2–A6 accepts revoked and remediated binaries. AT1 older binary accepted on a stateless runner. LB1–LB3 inconsistencies. |
| `RV4-B-arch-functions.{py,json,stderr}` | computed (architect's P4r4 functions) | AF1 route B with honest custodians; AF2 route S with honest signers; AF3 first binary by A2–A6 tooling | AF1: custodian and publisher stages `PASS`; `ACCEPTED`; world identical to VA4's route B. AF2 `ACCEPTED` (REJECTED held: refused; S1: refused). AF3: tooling `PASS`; full `verify-artifact` `ARTIFACT_REVOKED`. |
| `RV4-B-surface-probes.{py,json,stderr}` | executed (pack checker; real 4.1.5) | **U** unknown keys and files. **T** tunable-only kernel consumption. **P** pinned registered-digest mix with consumption. | U01/U02 exit 0 (wildcard informational); U03–U05, U07, U08 exit 2; U06 exit 0; U09/U10 add no problem. T exit 0 and no harm difference. P: mixed kernel exit 0, `reductions` silent, the `ASIA…` key file indexed and retrievable (fixed release: excluded). |
| `RV4-B-confinement-and-first-binary.{py,json,stderr}` | executed (real 4.1.5 as the command runner; real Git; bash) | **A** a `gov verify product` child plants `gov` on `PATH`, a `.bashrc` line and a git hook, none in the R-CONF-1 deny list. **B** first-binary procedure (c) self-report. | A: all writes succeed; planted `gov` runs first and writes a VTS anchor and confirmation; hook runs. B: TBM has no code digest; the planted binary passes (c); its digest differs from the attested one. |
| `r3-probe-copies/*.py` | copies (unmodified) | review r3 B and D probe scripts | SHA-256 below |
| `r3-rerun/*.{json,stderr}` | executed / computed | re-runs of those copies against revision 4 | A01 exit 3; A03 pins still written by the legacy child; A14 exit 2 ×10; A16 exit 3; I01–I09 as the architect's re-run; P2 reproduced; D lattice 0 unsound; D surface R01–R09 exit 2 |

### Copies of prior probes (unmodified; origin `release/root-of-trust/4.1.6-review-r3/`)

| SHA-256 | File | Origin |
|---|---|---|
| `703b806df5c829b1d1ca365c9a6f5d04aee72a8c515a919f86f845588d51c606` | `RV3-B-A01-precedence-immutable.py` | `B-trust-security/evidence/` |
| `2149077b7d19f9232f61b8071ef95d943aae9eb878c4d74169886056016e4493` | `RV3-B-A03-A14-A16-probes.py` | `B-trust-security/evidence/` |
| `48f373828e099cd1de2824dc349f1598ea961b890c5bd9cec02b31bd6566dec5` | `RV3-B-CSI-injections.py` | `B-trust-security/evidence/` |
| `1ac5b41541bc55f9b5db733ff66a9caa268b784967744c3ea0293c9104265efa` | `r2rerun-P2-gate-record-forgery.py` | `B-trust-security/evidence/` |
| `9fb4f746ae94aec53a3700dd69afe7d0f93f6c822c36ead6590d6c815cdf005c` | `RV3-D-precedence-lattice.py` | `D-synthesis/evidence/` |
| `f2986c620603cb06358f9bc9137ea4ff5d310dd0ec4331518b64a7f9e15da6a8` | `RV3-D-surface-forward-compat-and-removal.py` | `D-synthesis/evidence/` |

## Running

```sh
W=<worktree>; S=<fresh scratch dir>; LEG=<dir with gov-4.1.2 … gov-4.1.5>
E="env -i PATH=/usr/bin:/bin HOME=$S/home PYTHONDONTWRITEBYTECODE=1 REVIEW_REPO=$W"
cd $W/release/root-of-trust/4.1.6-review-r4/B-trust-security/evidence
$E python3 RV4-B-M-reference-model.py > RV4-B-M-reference-model.json
$E python3 RV4-B-arch-functions.py > RV4-B-arch-functions.json
$E GOV_REVIEW_SCRATCH=$S/surf GOV=$LEG/gov-4.1.5 python3 RV4-B-surface-probes.py > RV4-B-surface-probes.json
$E GOV_REVIEW_SCRATCH=$S/conf GOV=$LEG/gov-4.1.5 python3 RV4-B-confinement-and-first-binary.py > RV4-B-confinement-and-first-binary.json
# review r3 probes against revision 4 (copies)
for p in RV3-B-A01-precedence-immutable RV3-B-A03-A14-A16-probes RV3-B-CSI-injections r2rerun-P2-gate-record-forgery RV3-D-precedence-lattice; do
  $E GOV_REVIEW_SCRATCH=$S/r3 python3 r3-probe-copies/$p.py > r3-rerun/$p.json; done
$E python3 r3-probe-copies/RV3-D-surface-forward-compat-and-removal.py $S/r3/fc > r3-rerun/RV3-D-surface-forward-compat-and-removal.json
# architect's instruments
P=$W/release/root-of-trust/4.1.6
$E python3 $P/constitutional-surface/csi_check.py selftest --scratch $S/csi
$E python3 $P/evidence/P4r4-trust-state-model.py | cmp - $P/evidence/P4r4-trust-state-model.json
$E python3 $P/evidence/VA4-verify-artifact-source-scenarios.py | cmp - $P/evidence/VA4-verify-artifact-source-scenarios.json
$E GOV_REVIEW_SCRATCH=$S/p1r4 GOV=$LEG/gov-4.1.5 python3 $P/evidence/P1r4-project-strength-and-absence.py | cmp - $P/evidence/P1r4-project-strength-and-absence.json
```

Outputs were written to scratch and copied here with the path placeholders. The model and the architect-functions probe
take seconds; the surface probe about 30 s; the confinement probe a few seconds.

**Environment:** Python 3.12.3, PyYAML 6.0.1, git 2.43.0, Linux 6.6 (WSL2).

## Notes

- **Model independence.** `RV4-B-M-reference-model.py` was written from the pack text and does not import P4r4.
  - Its matrix classification assigns every accepting row to a residual the pack states (RS-1/RS-1c core, OP-7 (d),
    RS-2, RS-3, RS-4, RS-5), or to `UNSTATED`. No row is `UNSTATED`.
  - The `BC` section encodes the honest actors' stated checks: `05` §7 rules 2–7, `25` §9, `07` §7 and R-REL-6.
  - One modelling assumption is explicit: the verifier's REJECTED attestation either reaches the signers and the
    publisher or it does not. Both cases are reported.
- **Why AF1 matters.**
  - It uses only the architect's functions. It shows that the custodial pre-checks of `25` §9 pass on the draft for
    malicious bytes that carry a forged build attestation.
  - The resulting world is object-for-object VA4's "route B" row, which the pack presents as needing four stolen keys.
- **Stand-in consumer.**
  - The 4.1.5 binary consumes whatever kernel it is given. The surface probe's part P therefore demonstrates the
    consumption of the effective kernel that revision-4 rules select (`19` §5.2: the pinned value registered in the
    effective TPS), as P1r4 does for precedence.
- **Confinement probe.**
  - It runs the child through the legacy binary, which is unconfined, to show the writes and their later execution. The
    design comparison is with the revision-4 deny list: no written path is in it.
