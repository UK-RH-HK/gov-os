# Evidence — review r4 synthesis D (AR-0008)

**Scratch only.** Every probe ran under `…/scratchpad/ar-0008/` with `env -i`; `HOME`, `XDG_*` and `GOV_KERNEL_CACHE` in
scratch; `PYTHONDONTWRITEBYTECODE=1`; no other `GOV_*` in any child (reviewer C's library strips them). The real legacy
binaries were used read-only. The canonical checkout was never written. No RoT-1 binary exists: revision-4 behaviour is
established with the pack's checker, the architect's P4r4 and LR2 functions, reviewer C's `18` §9 re-encoding, and the
real 4.1.5 binary as the legacy actor. Absolute scratch paths in outputs are replaced by `<scratch>`, `<out>`,
`<worktree>` or `<scratchpad-path>`.

## Files

| File | Kind | Establishes |
|---|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | record | Git blob id and SHA-256 of every reviewed file at base `9349d8c`: the pack, the panel's directories, D-0007, D-0008, ARCH-0002, `docs/DECISIONS.md`, the review-r3 consolidated files, HO-0008, HO-0001, `AGENT_RUNS/README.md`, `cli/src/main.rs`, `runtime/src/project.rs` |
| `REPRODUCTION-LOG.json` | record | every reproduced instrument, its command, comparison and result; binary digests |
| `probes/repro_ab.sh` | runner | architect's instruments and reviewer B's probes, unmodified |
| `probes/repro_c.sh` | runner | reviewer C's probes, unmodified, with C's documented `AR7_WT` and `AR7_LEGACY_BIN` overrides |
| `probes/RV4-D-A01-nested-root-escalation.py`, `outputs/RV4-D-A01.json` | executed | D-A01: nested legacy installs from `governance/`, `governance/trust/`, `governance/trust/kernel/`; nested-root CITs; RoT-1 state, kernel check and strength vector |
| `probes/RV4-D-A02-pinned-retention-breadth.py`, `outputs/RV4-D-A02.json` | executed (checker) | D-A02: retention of superseded tool descriptor, invariant, schema and skill digests passes E7 and `reductions` |
| `probes/RV4-D-A03-oracle-regression-sensitivity.py`, `outputs/RV4-D-A03.json` | computed | D-A03: 20 single-line mutants of P4r4; P4r4 and VA4 run unmodified against each; 9 detected |
| `probes/RV4-D-A03b-distinguishing-scenarios.py`, `outputs/RV4-D-A03b.json` | computed | D-A03b: a distinguishing scenario for each of the 11 undetected mutants; 11 of 11 distinguish |

## Running

```sh
W=<worktree>; S=<fresh scratch>; LEG=<dir with gov-4.1.2 … gov-4.1.5>
# reproduction (set AR8_SCRATCH, AR8_WORKTREE and AR8_LEGACY_BIN)
bash probes/repro_ab.sh; bash probes/repro_c.sh
# held-out attacks
E="env -i PATH=/usr/bin:/bin HOME=$S/home PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 AR7_LEGACY_BIN=$LEG"
$E python3 -B probes/RV4-D-A01-nested-root-escalation.py $S/reproC/t/trees.json $S/a01 $W   # needs C's trees (repro_c.sh)
$E python3 -B probes/RV4-D-A02-pinned-retention-breadth.py $W $S/a02
$E python3 -B probes/RV4-D-A03-oracle-regression-sensitivity.py $W $S/a03
$E python3 -B probes/RV4-D-A03b-distinguishing-scenarios.py $W $S/a03b
```

**Environment:** Python 3.12.3, PyYAML 6.0.1, git 2.43.0, Linux 6.6 (WSL2).

## Notes

- **D-A01** copies reviewer C's R4 tree per case, imports C's `c4lib` (child environment, whole-tree maps, `18` §9
  re-encoding) and the architect's `LR2` module (its `18` §9 encoding, overlay readers and `csi_lib` strength functions).
  The kernel check compares the whole `governance/trust/kernel/` tree before and after, as `18` §6.1 step 5 does against
  the release content set.
- **D-A03** materialises each mutant as a copy of `P4r4-trust-state-model.py` with exactly one replacement (asserted to
  occur once) beside an unmodified copy of `VA4-verify-artifact-source-scenarios.py`, which loads P4r4 from its own
  directory. Detection compares each scenario's `holds` and each row's `as_expected` with the unmodified run.
- **D-A03b** reads the mutant table from D-A03's source and builds each scenario only from P4r4's constructors
  (`tss`, `pin`, `witness`, `release`, `attest`, `cert`, `build_att`, `artifact`, `tbm`, `tps`).
