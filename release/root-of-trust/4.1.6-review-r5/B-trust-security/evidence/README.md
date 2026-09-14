# Evidence — review r5 B (AR-0012)

Revision reviewed: `cdb4e14009bba60bea9b805563c1b60e84f30b4b`. Every probe ran against a scratch export of that commit
(`git archive`), never against the worktree or the canonical checkout.

## Environment and hygiene

- **Child environment.** `env -i PATH=/usr/bin:/bin`, with `HOME`, `TMPDIR`, `XDG_*` and `GOV_KERNEL_CACHE` in scratch and
  `PYTHONDONTWRITEBYTECODE=1` (every script also sets `sys.dont_write_bytecode`). No other `GOV_*` variable in any child;
  scripts that call the legacy binary strip `GOV_*` again.
  - RV5-B-A08 is the one exception: it runs with `HOME` set to the account home, so that the read-only rustup toolchain
    resolves. It writes only into its scratch directory.
- **Tools.** Python 3.12.3, PyYAML 6.0.1, cryptography 41.0.7, OpenSSL 3.0.13, git 2.43.0, rustc 1.98.1, gcc 13.3.0, Linux 6.6
  (WSL2).
- **Legacy binaries** (read-only), SHA-256:

  | Binary | SHA-256 |
  |---|---|
  | 4.1.2 | `dc924fb3293b3fdafbcfd1d87827a37315de8de75ed7f27431bee0aa74a767b7` |
  | 4.1.3 | `baba4e403dc23fe975ee2a277d0d2908e2aa7a54e4bd88dd2a323a2cb7d0fd89` |
  | 4.1.4 | `85f34cce2b43877f01da720c84ab3854b253b7959c26cac957e725d7d4e5b67f` |
  | 4.1.5 | `9169d7a8be41324a76c540ad440d4d7692e12cfedf3530a3f9895886021de915` |

- **No forced deletes.** Scratch directories were created fresh.

## Files

| File | Content |
|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | SHA-256 of every reviewed file at `cdb4e14`: the pack, D-0007, D-0008, ARCH-0002, `docs/DECISIONS.md`, review r4 (identical to `97a5545`), specialist `SYNTHESIS.md` |
| `rerun/RERUN-LOG.json` | re-execution of the architect's instruments and review r4/r3 probes: exit codes, output and committed SHA-256, comparison |
| `probes/rerun_arch.sh` | the commands behind `RERUN-LOG.json` (scratch paths of this session) |
| `probes/RV5-B-A01-first-admission-channel.py` → `outputs/…json` | A01, A02, A03, A14 (executed; reference executor unmodified) |
| `probes/RV5-B-A04-calculator-extensions.py` → `outputs/…json` | A04 (part L), A07 (part R), A06 (part P and P4r5 computed rows), A08 (part I), A19 (part C) (computed; CS5 and P4r5 unmodified) |
| `probes/RV5-B-A05-source-identity.py` → `outputs/…json` | A05 (executed; real Git) |
| `probes/RV5-B-A08-build-image-selects-bytes.py` → `outputs/…json` | A08 (executed; rustc and gcc) |
| `probes/RV5-B-A09-floor-class-kernels.py` → `outputs/…json` | A09, A10, A11, A16 (executed; pack checker and real 4.1.5) |
| `probes/RV5-B-A12-machine-classes.py` → `outputs/…json` | A12, A13 (computed; P4r5 and P4r4 functions unmodified) |

## How to re-run

From a directory holding the probes:

```text
E="env -i PATH=/usr/bin:/bin HOME=<scratch>/home TMPDIR=<scratch>/tmp PYTHONDONTWRITEBYTECODE=1 GOV_KERNEL_CACHE=<scratch>/kcache REVIEW_REPO=<export of cdb4e14>"
$E SCRATCH=<scratch>/a01 python3 -B RV5-B-A01-first-admission-channel.py > RV5-B-A01-first-admission-channel.json
$E python3 -B RV5-B-A04-calculator-extensions.py > RV5-B-A04-calculator-extensions.json
$E SCRATCH=<scratch>/a05 python3 -B RV5-B-A05-source-identity.py > RV5-B-A05-source-identity.json
env -i PATH=/usr/bin:/bin HOME=<account home> TMPDIR=<scratch>/tmp PYTHONDONTWRITEBYTECODE=1 SCRATCH=<scratch>/a08 python3 -B RV5-B-A08-build-image-selects-bytes.py > RV5-B-A08-build-image-selects-bytes.json
$E GOV=<legacy-bin>/gov-4.1.5 SCRATCH=<scratch>/a09 python3 -B RV5-B-A09-floor-class-kernels.py > RV5-B-A09-floor-class-kernels.json
$E python3 -B RV5-B-A12-machine-classes.py > RV5-B-A12-machine-classes.json
```

## Determinism

A second run of A01, A04, A09 and A12 was byte-identical to the committed outputs. A05 part 2 is time-dependent by design:
its verdicts are stable, but its archive digests change between runs. A08 is deterministic in its verdicts; its digests
depend on the local compiler.

## SHA-256 of committed evidence

| SHA-256 | File |
|---|---|
| `34de320fa2841bc1cba6924e6b886778e1a3dd565db13574f320386353ffbcc6` | `probes/RV5-B-A01-first-admission-channel.py` |
| `e676cfeeffef1a3007e262b027575faff674a5107b6b3989bcdb1b9e31818b10` | `probes/RV5-B-A04-calculator-extensions.py` |
| `95aa21dae84a1c7e3f900b68a4fa677c5557025f9f7b56734c403b0f92d374ed` | `probes/RV5-B-A05-source-identity.py` |
| `8706c7fb302386925e9b60f4c4f2b6a73f33c4cb4b2a07f1cadacd512cdc05bc` | `probes/RV5-B-A08-build-image-selects-bytes.py` |
| `0157d7be298934d45bf8231845161ddf219a6e7e8897ee207343c2d8be0e427b` | `probes/RV5-B-A09-floor-class-kernels.py` |
| `da7d64602305b94b34cbb0f988347e57593a279a5319c21791653cd364a28572` | `probes/RV5-B-A12-machine-classes.py` |
| `8c3b76e542af3e51bfc1bc03a625cd426a8444a3332d040f152ed571da8d2ae1` | `probes/rerun_arch.sh` |
| `469f9d3ca5a65d7bcff251b58b7368da1f0b4a58c0243ad2515bcc88af4b4747` | `outputs/RV5-B-A01-first-admission-channel.json` |
| `007d89fe64028adefa38f4abd243a142d70e534e93f27fb03135345c51ac52e7` | `outputs/RV5-B-A04-calculator-extensions.json` |
| `e286e8390b6ba861fb0c61892dbdbf53b138c6ea4e498036dbe959b9756d73a7` | `outputs/RV5-B-A05-source-identity.json` |
| `cf5b65b5881ae43f21bbcfdbb160d77c6f23c7fd876acc954258f99edab0c60a` | `outputs/RV5-B-A08-build-image-selects-bytes.json` |
| `a1d90a87f52f71ae601f4bdc9480ab0c1828340a1876a9e08d2b1a0228abbbc0` | `outputs/RV5-B-A09-floor-class-kernels.json` |
| `1af2220bb36f056679014b3a28ac7484c6a1758f6b1a0ec2efc9b26fe4f5814c` | `outputs/RV5-B-A12-machine-classes.json` |
| `7d56e27eb7cd3987bb59b97426a7ceda2e6b4f9537fe525277c73d7381d62f2b` | `rerun/RERUN-LOG.json` |
| `5c81fa0a3a552da26aa85170d96fe44fd36396e090ca244a8e5fb0b84fb24520` | `REVIEWED-CONTENT-DIGESTS.txt` |

## Attribution

- RV5-B-A09 re-types `consume`, `rel_copy`, `set_patterns` and the TPS v2 member classification from
  `4.1.6/evidence/r5/REG5-release-scoped-registration.py`. REG5 follows review r4 B `RV4-B-surface-probes.py` part P and
  review r4 D `RV4-D-A02`.
- RV5-B-A01 follows the statement shapes read by `4.1.6/evidence/r5/gov_admit_reference.py` and the key derivation of
  `FA5-first-admission.py`.
- No instrument of the pack or of an earlier review was modified.
