# Evidence — root-of-trust specialist B (AR-0010)

**Scratch only.**
- Probes ran under `…/scratchpad/ar-0010/` with `env -i`.
- `HOME`, `XDG_*`, `AR10_SCRATCH`, `GOV_REVIEW_SCRATCH` and `GOV_KERNEL_CACHE` pointed into scratch.
- `PYTHONDONTWRITEBYTECODE=1`; no other `GOV_*` variable reached any child.

**Read-only inputs.**
- The worktree was read only, except this directory.
- Legacy binaries were used read-only (SHA-256 in F0).

**Output hygiene.** Absolute scratch paths in outputs are replaced by `<scratch>`, `<worktree>`, `<legacy-bin>` or
`<scratchpad-path>`.

**No RoT-1 binary exists.** Behaviour is established with:
- the revision-4 checker, unmodified, run on projections;
- reviewer B's review-r4 reference model, loaded unmodified;
- this run's models;
- the real 4.1.5 binary as consumer;
- real Git and real `cargo`.

## Files

| File | Kind | Establishes | Result |
|---|---|---|---|
| `F0-baseline-reproduction.json` | record | reviewer and architect instruments re-run unchanged before modelling | B model, VA4, D-A02 and B surface probes identical; CSI self-test 56/56; review-r3 copies (A01, CSI injections, lattice, forward-compat/removal) identical after path normalisation |
| `F1-tcb-fact-derivation.{py,json,stderr}` | computed | minimal capability sets for an accepted malicious binary: revision 4 (reviewer B's enumeration re-run) and the alternative for every OC-1 × OC-2 × OP-4 × REJECTED-delivery answer | revision 4 `{ba, pipeline}`; alternative ≥ 2 first-hand establishers in every minimal set (32 configurations, 0 violations) |
| `F2-first-tcb-admission.{py,json,stderr}` | computed | independent admission: RV4-B-A03/A04, Phase 4, CI image, RV4-D-A04, channels, admitter substitution, review-r3 anchor probes through AP; mutation self-check; first-install minimal sets | 32/32 scenarios hold; 18/18 mutants detected; `{ch1, ch2}`, `{ba1, ba2, ts}`, `{ba1, ba2, pipeline}` |
| `F3-release-scoped-registration.{py,json,stderr}` | executed | single-valued sequence-scoped registration via projections onto the unmodified checker; part P and D-A02 T1–T4 shapes; open vs closed ranges; reversion and rewrite reductions; consumption on real 4.1.5 | forged mixed release exit 3 (both forms); retention exit 0; E2-open stale-TPS residual exit 0; reductions exit 6 / 0 with history; consumer excludes the `ASIA…` file |
| `F4-external-measurement.{py,json,stderr}` | executed | source identity by `git archive` vs canonical content digest; planted self-reporting binary; measure-then-install | commit archive binds the commit id; tree archive is time-stamped; canonical digest equal across repositories and changes on a moved tag; candidate never executed; buffer install holds, path re-read does not |
| `F5-reproducible-build-part1.sh`, `F5-reproducible-build-part2.sh`, `F5-reproducible-build.txt` | executed | bit-for-bit reproducibility of `gov` from `git archive` of the base commit across source paths and Cargo home paths, plain and path-remapped | plain differs across Cargo homes (188 path strings); remapped identical across 4 builds (0 path strings) |

## Attribution

- **F1 and F2** load `release/root-of-trust/4.1.6-review-r4/B-trust-security/evidence/RV4-B-M-reference-model.py` by path,
  unmodified: `grants`, `vkeys`, `assess`, `trust_state`, `ingest`, `negatives`, statement constructors, `minimal_sets`.
- **F3's consumer functions** (`consume`, `rel_copy`, `db_paths`, `gov`, `git`) are adapted from
  `RV4-B-surface-probes.py` part T and part P. Its target fixes are copied from
  `D-synthesis/evidence/probes/RV4-D-A02-pinned-retention-breadth.py`.
- **F4's planted binary** re-creates `RV4-B-confinement-and-first-binary.py` part B.

## Running

```sh
W=<worktree>; S=<fresh scratch dir>; LEG=<dir with gov-4.1.2 … gov-4.1.5>
EV=$W/release/root-of-trust/4.1.6-alternatives-r5/specialist-b/evidence
E="env -i PATH=/usr/bin:/bin HOME=$S/home PYTHONDONTWRITEBYTECODE=1 AR10_SCRATCH=$S GOV=$LEG/gov-4.1.5"
$E python3 -B $EV/F1-tcb-fact-derivation.py        > F1-tcb-fact-derivation.json        # ~2 s
$E python3 -B $EV/F2-first-tcb-admission.py        > F2-first-tcb-admission.json        # ~1 s
$E python3 -B $EV/F3-release-scoped-registration.py > F3-release-scoped-registration.json # ~12 s (real 4.1.5)
$E python3 -B $EV/F4-external-measurement.py       > F4-external-measurement.json       # ~2 s
env -i PATH=/usr/bin:/bin bash $EV/F5-reproducible-build-part1.sh $W $S/repro   # 4 release builds, ~40 s each
env -i PATH=/usr/bin:/bin bash $EV/F5-reproducible-build-part2.sh $S/repro      # 4 more builds
```

**Script assumptions.**
- F5 copies `~/.cargo/registry` into scratch Cargo homes and reads the toolchain from `~/.rustup`. It builds with
  `--offline --locked`.
- F1–F4 derive the worktree from their own location unless `AR10_WORKTREE` is set.

**Environment:** Python 3.12.3, PyYAML 6.0.1, git 2.43.0, cargo 1.98.1, rustc 1.98.1, Linux 6.6 (WSL2).
