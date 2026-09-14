# Evidence — review r5 synthesis D (AR-0014)

Revision reviewed: `cdb4e14009bba60bea9b805563c1b60e84f30b4b`. Panel: reviewer B `248f12a`, reviewer C `840d583`. Every probe
ran against a scratch export of `cdb4e14`, never against the worktree or the canonical checkout.

## Environment and hygiene

- **Child environment:** `env -i PATH=/usr/bin:/bin`, with `HOME`, `TMPDIR`, `XDG_*` and `GOV_KERNEL_CACHE` in scratch and
  `PYTHONDONTWRITEBYTECODE=1`. No other `GOV_*` variable is set; the probes that call the legacy binary strip `GOV_*`
  again.
- **Tools:** Python 3.12.3, PyYAML 6.0.1, cryptography 41.0.7, OpenSSL 3.0.13, git 2.43.0, rustc 1.98.1, Linux 6.6 (WSL2).
- **Legacy binaries (read-only), SHA-256:**

  | Binary | SHA-256 |
  |---|---|
  | 4.1.2 | `dc924fb3293b3fdafbcfd1d87827a37315de8de75ed7f27431bee0aa74a767b7` |
  | 4.1.3 | `baba4e403dc23fe975ee2a277d0d2908e2aa7a54e4bd88dd2a323a2cb7d0fd89` |
  | 4.1.4 | `85f34cce2b43877f01da720c84ab3854b253b7959c26cac957e725d7d4e5b67f` |
  | 4.1.5 | `9169d7a8be41324a76c540ad440d4d7692e12cfedf3530a3f9895886021de915` |

- **No forced deletes:** scratch directories were created fresh.
- **Paths:** absolute scratch paths in committed files are replaced by `<scratch>`, `<scratchpad>`, `<repo>` and
  `<legacy-bin>`.

## Files

| File | Content |
|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | SHA-256 and Git blob id of every reviewed file at base `59c1e5c`: the pack, reviewer B's and C's directories, review r4's consolidated files, the specialist `SYNTHESIS.md`, D-0007, D-0008, ARCH-0002, `docs/DECISIONS.md`, HO-0014, HO-0001, `AGENT_RUNS/README.md`. Also the legacy binaries. |
| `reproduction/REPRODUCTION-LOG.json` | every re-executed instrument and probe: exit, SHA-256 of the re-run and committed outputs, comparison; reviewer C's prior-probe reproduction comparison; determinism of this review's probes |
| `reproduction/rerun_arch.sh` | commands behind the architect-instrument and review r4/r3 re-runs (adapted from reviewer B's `rerun_arch.sh`) |
| `reproduction/cmp_arch.py` | first-pass comparison script for those re-runs |
| `probes/RV5-D-A01-registered-content-not-first-hand.py` → `outputs/…json` | D-A01: computed on P4r5 (ceremony, V8 and E7 as written, with restrictor variants, OP-4 "no"); executed with the checker and real 4.1.5 |
| `probes/RV5-D-A03-user-writable-install-anchoring.py` → `outputs/…json` | D-A03: reference `gov_run` and P4r4 decision rule |
| `probes/RV5-D-A04-conformance-vector-gaps.py` → `outputs/…json` | D-A04: reference executor (real Ed25519) and P4r5 on AP-4/AP-5 rows R1–R4; coverage in committed vectors |
| `probes/RV5-D-A05-forward-compat-new-constitutional-file.py` → `outputs/…json` | D-A05: checker on a new kernel-shipped contract file set (N1–N5) |
| `probes/RV5-D-A07-plan-regression-detection.py` → `outputs/…json` | D-A07: calculator goals and atoms, plan rows, register rows per defect |

RV5-D-A02, A06 and A08 are design attacks. Their statements and references are in `../03-HELDOUT-ATTACKS-RV5-D.md`.

## How to re-run

From a directory holding the probes, with `R` an export of `cdb4e14` and `L` the legacy binary directory:

```text
E="env -i PATH=/usr/bin:/bin HOME=<scratch>/home TMPDIR=<scratch>/tmp PYTHONDONTWRITEBYTECODE=1 GOV_KERNEL_CACHE=<scratch>/kcache REVIEW_REPO=$R"
$E GOV=$L/gov-4.1.5 SCRATCH=<scratch>/a01 python3 -B RV5-D-A01-registered-content-not-first-hand.py > RV5-D-A01-registered-content-not-first-hand.json
$E SCRATCH=<scratch>/a03 python3 -B RV5-D-A03-user-writable-install-anchoring.py > RV5-D-A03-user-writable-install-anchoring.json
$E GOV=$L/gov-4.1.5 SCRATCH=<scratch>/a04 python3 -B RV5-D-A04-conformance-vector-gaps.py > RV5-D-A04-conformance-vector-gaps.json
$E SCRATCH=<scratch>/a05 python3 -B RV5-D-A05-forward-compat-new-constitutional-file.py > RV5-D-A05-forward-compat-new-constitutional-file.json
$E python3 -B RV5-D-A07-plan-regression-detection.py > RV5-D-A07-plan-regression-detection.json
```

- **Export.** Use an export that no instrument has written into. `FA5-first-admission.py` and `SRC5-source-identity.py`
  rewrite their own JSON inside the evidence directory they run from.
- **Determinism.** A second run of each probe was byte-identical.

## SHA-256 of committed probes and outputs

| SHA-256 | File |
|---|---|
| `14108f8d8e2e217f05f90cdc15065a7e8d22548fa941739ed57b276b3d79a9b5` | `probes/RV5-D-A01-registered-content-not-first-hand.py` |
| `86100c127b4e6fbe1c84d807653692c10c01742e09176b3635f317f496f07a05` | `probes/RV5-D-A03-user-writable-install-anchoring.py` |
| `c18d05aca3c8e47afc953ebdba4c3f4d4e7abfc975c5cfeaa491376609c6886d` | `probes/RV5-D-A04-conformance-vector-gaps.py` |
| `8523537a08b97e8eadd6a62b6dda8307e7e7733d25dfda1cf0873b2caba7cc50` | `probes/RV5-D-A05-forward-compat-new-constitutional-file.py` |
| `164990a86be1d1231406486fbfe2644308baceffc0c8cd15bf52af36d114acae` | `probes/RV5-D-A07-plan-regression-detection.py` |
| `d791fb089a46e143eea65e42b305eac2f4eb138b9411394bdf6540e89c36f1c9` | `outputs/RV5-D-A01-registered-content-not-first-hand.json` |
| `d9d3c2691aca83faee6236d602ba56222fc220bb89d6dd7f10a1c93de964ddf2` | `outputs/RV5-D-A03-user-writable-install-anchoring.json` |
| `163069ac31380912b6e742f235832e0f906f6a730cfea9641e069496eecc3cf8` | `outputs/RV5-D-A04-conformance-vector-gaps.json` |
| `6586c60f5715b9562af05dacc966247035c988f57107f9982f63186059f9ab03` | `outputs/RV5-D-A05-forward-compat-new-constitutional-file.json` |
| `f5e8907ea7931f9487cf97eb5e49a64f68301df2d3dbdd6a4173e3265a86078b` | `outputs/RV5-D-A07-plan-regression-detection.json` |

## Attribution

- RV5-D-A01 part B and RV5-D-A05 follow reviewer B's `RV5-B-A09-floor-class-kernels.py` for the checker helpers, and
  RV5-D-A01 also for the consumer set-up. B's code follows the architect's REG5 and review r4 reviewer B part P.
- RV5-D-A04 executes FA5's statement builders unmodified up to its "CONFORMANCE VECTORS" marker.
- Every probe loads P4r5, P4r4, CS5 and `gov_admit_reference.py` unmodified.
- No instrument of the pack, of the panel or of an earlier review was modified.
