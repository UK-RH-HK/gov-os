# Evidence — review r6 synthesis D (AR-0018)

- **Revision reviewed:** `4106885dadebac55596067a2586cf4d3097fc025`.
- **Exports:** every probe and re-run executed against scratch exports (`git archive`) of this review's base `b9bed32`. At that
  base the pack, D-0008, ARCH-0002 and `docs/DECISIONS.md` are identical to `4106885`, the implementation to `da9c851`, and the
  panel directories to `5128086` (B) and `02bb905` (C) (checked with `git diff --quiet`).
  - `export`: the working export.
  - `pristine`: an unmodified export used as the comparison source.
- Nothing ran in the worktree or the canonical checkout.

## Environment and hygiene

- **Child environment.** Every child ran under `env -i PATH=/usr/bin:/bin`, with `HOME`, `TMPDIR`, `XDG_*` and `GOV_KERNEL_CACHE`
  in scratch, `PYTHONDONTWRITEBYTECODE=1`, `GIT_CONFIG_NOSYSTEM=1` and `python3 -B`. No `GOV_*` variable was set, except
  `GOV_KERNEL_CACHE` into scratch. `GOV` names the legacy binary path for instruments that use it. Reviewer C's matrix sets
  `GOV_*` variables only in its own `P-ENV` rows, as its object of test.
- **Exceptions, as in the panel's runs.**
  - The architect's ENV6 and reviewer B's A02 read the read-only rustup toolchain from the account home (`ENV6_ACCOUNT_HOME`,
    `A02_ACCOUNT_HOME`). The review r5 `RV5-B-A08` re-run sets `HOME` to the account home for the same reason. All write only
    under scratch.
  - Reviewer C's `register6.py` reads `cli/src/main.rs` at the four release commits with `git show` from this review's worktree
    (read-only).
- **Tools.** Python 3.12.3, PyYAML 6.0.1, cryptography 41.0.7, OpenSSL 3.0.13, git 2.43.0, rustc 1.98.1, gcc 13.3.0, Linux 6.6
  (WSL2).
- **Legacy binaries.** Read-only scratch copies of `gov-4.1.{2,3,4,5}`; SHA-256 in `REVIEWED-CONTENT-DIGESTS.txt` section F.
- **No forced deletes.** No `rm -rf` or `rm -f` was used. A failed first launch of reviewer C's chain (a missing scratch input) was
  moved aside. Reviewer C's own probes remove their per-row scratch copies with Python `shutil.rmtree`, as C disclosed.
- **No helper sessions.**
- **Paths.** This review's probe outputs replace scratch paths with `<scratch>` and `<export>`. Re-run logs and comparison files
  keep the scratch paths as run.

## Files

| Path | Content |
|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | SHA-256 of every reviewed file from Git objects: the pack, D-0007, D-0008, ARCH-0002 and `docs/DECISIONS.md` at `4106885`; reviewer B at `5128086`; reviewer C at `02bb905`; the review r5 consolidated files at `d1228cb`; the alternatives synthesis and the three orchestration files read, at `b9bed32`; legacy binaries |
| `probes/d6world.py` | shared loader of FA5's world on the revision-6 executor (FA6's substitutions, copied with attribution) |
| `probes/RV6-D-A01-…py` … `RV6-D-A10-…py` | this review's held-out attacks (`03-HELDOUT-ATTACKS-RV6-D.md`) |
| `probes/rerun_arch_r6.sh`, `rerun_B.sh`, `rerun_C.sh`, `rerun_r5_probes.sh` | re-execution scripts (architect instruments; reviewer B probes; reviewer C probes; review r5 decisive probes). The first and fourth are adapted from reviewer B's scripts, with attribution. |
| `probes/compare_arch.py` | byte and leaf comparison of the architect and reviewer B re-runs (adapted from reviewer B's `compare_reruns.py`, with attribution) |
| `outputs/RV6-D-A*.json` | outputs of the ten attacks. `RV6-D-A03.first-run-probe-error.json` is the first A03 run, whose inventory row listed two digests and was refused `REGISTRATION_NOT_SINGLE_VALUED` (probe error; kept for the record). |
| `reproduction/arch-log.tsv`, `B-log.tsv`, `C-log.tsv`, `r5probes-log.tsv` | id, exit code, seconds, SHA-256 of output |
| `reproduction/compare-arch-B.json` | architect instruments and reviewer B probes against their committed outputs |
| `reproduction/compare-r5probes.json` | review r5 decisive probes against review r5's committed outputs and reviewer B's revision-6 re-runs |
| `reproduction/compare-C.json` | reviewer C probes against C's committed outputs |
| `reproduction/C-matrix6-summary.json` | this review's `matrix6` summary (the rows file stays in scratch) |

## How to re-run

With `S` a fresh scratch root holding `export` and `pristine` (`git archive` of the base) and `legacy` (the four binaries):
1. edit `S` at the top of each `rerun_*.sh`;
2. run the four scripts;
3. run each attack as:

```text
env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache \
  REVIEW_REPO=$S/export SCRATCH=$S/work/D GOV=$S/legacy/gov-4.1.5 python3 -B RV6-D-A0n-….py > RV6-D-A0n-….json
```

The attacks are deterministic in their verdicts. A02, A07 and A08 write temporary stores under `SCRATCH`.
