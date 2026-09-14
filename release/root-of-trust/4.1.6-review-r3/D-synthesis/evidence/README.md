# Evidence — review r3 synthesis D (AR-0004)

All probes run in scratch only.

- **Repository.** Read, never written, except this directory and the review's top-level files.
- **Child environment.** `env -i`, so no `GOV_*` variables; `HOME`, `XDG_*` and `GOV_KERNEL_CACHE` point into scratch; `PYTHONDONTWRITEBYTECODE=1`.
- **Legacy binaries.** Used read-only; their SHA-256 digests are in `REPRODUCTION-LOG.json`.
- **No RoT-1 binary exists.** Revision-3 behaviour is established with the pack's own checker and lattice, the architect's own model (loaded unmodified), reviewer B's model (reproduced byte-identical), and the real 4.1.5 binary as a consumer.
- **Placeholders.** In committed outputs, absolute scratch paths are replaced by `<scratch>`, the legacy binary directory by `<legacy-bin>` and this worktree by `<worktree>`.

## Files

| File | Kind | What it establishes | Result |
|---|---|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | record | SHA-256 and Git blob ids of 188 reviewed files at this review's base and at their origin commits: the pack, D-0007, D-0008, ARCH-0002 and DECISIONS.md at `ca77a43`; B at `7d8c73a`; C at `9e013c1`; review r2 at `e5a6b8a` | every blob identical to its origin |
| `REPRODUCTION-LOG.json` | record | the 14 re-runs of the panel's and architect's probes, with the comparison used | 14 of 14 reproduced |
| `RV3-D-precedence-lattice.{py,json,stderr}` | computed (pack `csi_lib.py`) | D-A01 soundness of the `23` §4 order; D-A02 TPS tightening | 5 unsound pairs; TPS tightening not a computed reduction for all 5 modes |
| `RV3-D-oracle-anchor-artifact.{py,json,stderr}` | computed (architect's P4r3, unmodified) | D-A11 oracle sensitivity; D-A12 anchor bypass; D-A13 A7 with a realisable construction; D-A15 revoked binary on pinned CI | 34/34 under both anchor semantics; bypass under sequence semantics; `BINARY_T0_ROLLBACK` under the TSS high-water; revoked binary accepted |
| `RV3-D-surface-forward-compat-and-removal.{py,json,stderr}` | executed (pack `csi_check.py run_check`) | D-A09 forward compatibility F01–F12; D-A10 removal R01–R09 | F as expected; every R exit 0; R07 66/85 rules join to `immutable` |
| `RV3-D-legacy-git-restore.{py,json,stderr}` | executed (real 4.1.5, Git) | D-A05 Git restore of legacy paths; D-A06 legacy CIT writing RoT-1 paths; D-A07 untracking idiom | verified legacy install, post-migration-classified file retrievable; `governance/trust` and overlay mutated; occupation absent in fresh clone |

## Running

```sh
W=<worktree>; S=<fresh scratch dir>; LEG=<dir with gov-4.1.2 … gov-4.1.5>
E="env -i PATH=/usr/bin:/bin HOME=$S PYTHONDONTWRITEBYTECODE=1 REVIEW_REPO=$W"
cd $W/release/root-of-trust/4.1.6-review-r3/D-synthesis/evidence
$E python3 RV3-D-precedence-lattice.py > RV3-D-precedence-lattice.json
$E python3 RV3-D-oracle-anchor-artifact.py > RV3-D-oracle-anchor-artifact.json
$E python3 RV3-D-surface-forward-compat-and-removal.py $S/fc > RV3-D-surface-forward-compat-and-removal.json

# RV3-D-legacy-git-restore.py needs reviewer C's L3 layout built from a real 4.1.5 project.
# C's scripts hard-code C's worktree in lib.py (REPO): copy them to scratch and set REPO to $W first.
mkdir -p $S/c && cp ../../C-compat-transaction/evidence/*.py $S/c/ && sed -i "s#^REPO = .*#REPO = \"$W\"#" $S/c/lib.py
env -i PATH=/usr/bin:/bin HOME=$S PYTHONDONTWRITEBYTECODE=1 python3 $S/c/build_base.py $S/run   # prints base and L3 (directory must not exist)
env -i PATH=/usr/bin:/bin HOME=$S PYTHONDONTWRITEBYTECODE=1 python3 RV3-D-legacy-git-restore.py $S/git $S/run/L3 $LEG/gov-4.1.5 > RV3-D-legacy-git-restore.json
```

The legacy probe takes about a minute. The others take seconds.

**Environment used:**
- Python 3.12.3, PyYAML 6.0.1;
- git 2.43.0;
- Linux 6.6 (WSL2), ext4.

## Notes

- **RV3-D-A11 and D-A12 use the architect's own model.** The script `exec`s the committed `P4r3-trust-state-model.py` text. For the chain-inclusion variant it replaces only `trust_state` (to expose the effective chain) and `freshness`. The committed model file is not edited.
- **RV3-D-A13 construction.** The artefact reference lives in a TSS later than the one the binary's TBM names. This is the only realisable order, because a TBM naming the TSS that references the artefact would require a hash cycle.
- **RV3-D-A09 fixture fixes.** Two corrections were made during this review, before the recorded run:
  - the Gate W precedence rules now use full keys, because `require_*` is not a legal one-segment wildcard and the first run failed lint;
  - F07 now gives its order inline, because the checker reads `order` as a list and a name string is not one.
- **RV3-D-A06 CIT chain.** The first recorded attempt stopped at gate presentation and at a missing index. The committed run adds `rebuild-memory`, `gate present` and `decide`, the steps the legacy binary itself requires.
