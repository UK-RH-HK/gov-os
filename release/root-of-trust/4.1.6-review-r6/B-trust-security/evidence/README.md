# Evidence — review r6 B (AR-0016)

Revision reviewed: `4106885dadebac55596067a2586cf4d3097fc025`. Every probe and re-run executed against scratch exports of that
commit (`git archive`): one working export and one pristine export used for comparisons and for this review's probes. Nothing
ran against the worktree or the canonical checkout.

## Environment and hygiene

- **Child environment.** `env -i PATH=/usr/bin:/bin`, with `HOME`, `TMPDIR`, `XDG_*` and `GOV_KERNEL_CACHE` in scratch,
  `PYTHONDONTWRITEBYTECODE=1`, `GIT_CONFIG_NOSYSTEM=1`, `python3 -B`. No `GOV_*` variable was set in any child (`GOV` names the
  legacy binary path for instruments that use it).
- **Exceptions.**
  - The re-run of `RV5-B-A08` sets `HOME` to the account home, as review r5 documented, so that the read-only rustup
    toolchain resolves.
  - `RV6-B-A02` and the architect's ENV6 read the toolchain from the account home (`A02_ACCOUNT_HOME`, `ENV6_ACCOUNT_HOME`)
    and write only under their scratch roots.
- **Tools.** Python 3.12.3, PyYAML 6.0.1, cryptography 41.0.7, OpenSSL 3.0.13, git 2.43.0, rustc 1.98.1, gcc 13.3.0,
  Linux 6.6 (WSL2).
- **Legacy binaries** (read-only): SHA-256 in `REVIEWED-CONTENT-DIGESTS.txt` section D (equal to review r5's).
- **No forced deletes.** Scratch directories were created fresh.
- **Paths.** Outputs replace scratch paths with `<scratch>`, `<scratchpad>`, `<export>` or `<home>`. The shell scripts, and
  `compare_reruns.py`, keep this session's scratch paths as run. `RV6-B-A02`'s default account home is the account path it
  ran with.
- **One failed launch, disclosed.** The first background launch of `RV6-B-A12` ran from the default working directory and could
  not find the script. It wrote only its stderr into scratch. It was re-launched with an absolute path; the committed output is
  from that run.
- **No helper sessions.**

## Files

| File | Content |
|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | SHA-256 of every reviewed file, from Git objects: the pack, D-0007, D-0008, ARCH-0002, `docs/DECISIONS.md` and the 4.1.5 runtime files read, at `4106885`; review r5 at `d1228cb`; the three orchestration files read, at the review base; legacy binaries |
| `probes/rerun_arch_r6.sh` | re-execution of every revision-6 architect instrument and the retained revision-5 instruments |
| `probes/rerun_r5_probes.sh` | review r5 decisive probes (B-A01, A04, A05, A08, A09, A12; D-A01, A03, A04, A05, A07), unmodified, against revision 6 |
| `probes/compare_reruns.py` → `rerun/COMPARISON.json` | byte and leaf comparison of every re-run with its committed output |
| `rerun/architect-instruments-log.tsv`, `rerun/review-r5-probes-log.tsv` | id, exit code, seconds, SHA-256 of output |
| `rerun/r5-probe-outputs-that-differ/` | the four review r5 probe outputs that are not byte-identical (A05 time-dependent digests; A08 compiler-dependent digest; D-A03 and D-A07 pack-text rows changed by revision 6) |
| `probes/RV6-B-A01-first-contact-selectors.py` → `outputs/…json` | A01, A05, A06, A13 (executed reference executor; computed CS6) |
| `probes/RV6-B-A02-environment-manifest-author.py` → `outputs/…json` | A02, A07, A08, A09 (executed real toolchain; computed CS6) |
| `probes/RV6-B-A03-generated-statement-rendering.py` → `outputs/…json` | A03 (computed; `statements_check.py` executed on a scratch pack copy) |
| `probes/RV6-B-A04-readmission-rollback.py` → `outputs/…json` | A04 (executed reference executor) |
| `probes/RV6-B-A10-surface-classes.py` → `outputs/…json` | A10 (executed checker) |
| `probes/RV6-B-A11-machine-classes-r6.py` → `outputs/…json` | A11 (computed P4r6/P4r5/P4r4) |
| `probes/RV6-B-A12-key-subsets-below-threshold.py` → `outputs/…json` | A12 (computed CS6 acceptance function) |

## How to re-run

From the probe directory, with `S` a fresh scratch root, `R` a `git archive` export of `4106885`, and `L` the legacy binary
directory:

```text
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 REVIEW_REPO=$R"
$E SCRATCH=$S/a01 GOV=$L/gov-4.1.5 python3 -B RV6-B-A01-first-contact-selectors.py > RV6-B-A01-first-contact-selectors.json
$E SCRATCH=$S/a02 A02_ACCOUNT_HOME=<account home> python3 -B RV6-B-A02-environment-manifest-author.py > RV6-B-A02-environment-manifest-author.json
$E SCRATCH=$S/a03 python3 -B RV6-B-A03-generated-statement-rendering.py > RV6-B-A03-generated-statement-rendering.json
$E SCRATCH=$S/a04 GOV=$L/gov-4.1.5 python3 -B RV6-B-A04-readmission-rollback.py > RV6-B-A04-readmission-rollback.json
$E SCRATCH=$S/a10 python3 -B RV6-B-A10-surface-classes.py > RV6-B-A10-surface-classes.json
$E python3 -B RV6-B-A11-machine-classes-r6.py > RV6-B-A11-machine-classes-r6.json
$E python3 -B RV6-B-A12-key-subsets-below-threshold.py > RV6-B-A12-key-subsets-below-threshold.json
```

- The re-run scripts take the same shape; edit `S` at their top.
- Outputs are then sanitised by replacing scratch paths with placeholders.

## Determinism

- **Stable.** A01, A03, A04, A10, A11 and A12 are deterministic in their verdicts and results. A01 and A03 were run twice
  (after an edit that extended A01 part C and corrected A03's verdict names); the committed outputs are from the final runs.
- **A02.** Deterministic in verdicts; its binary digests depend on the local compiler. It was run twice; the second run
  corrected one reporting expression (A08 `injected`) and produced identical verdicts and digests.

## SHA-256 of committed evidence

| SHA-256 | File |
|---|---|
| `7e61c94c65f14cdfbf99e84781839b5ecad4502f550b895dd445a1fc40e1716a` | `REVIEWED-CONTENT-DIGESTS.txt` |
| `52a91718bab499463e0233fd5c4c70a7fc353c5ee5cc540f4d431777bedc6c05` | `outputs/RV6-B-A01-first-contact-selectors.json` |
| `6e807f6fb99f52b5292b3d4d6acbed5a774d52bc2140d13aaa9c9cb04f5734f1` | `outputs/RV6-B-A02-environment-manifest-author.json` |
| `583415e8618641de5abd31d98944c565d3e2f12c526d8a13b92764c39f630428` | `outputs/RV6-B-A03-generated-statement-rendering.json` |
| `556429b4a2aa46fce469afd760538d061cc88b5e55c4df89a8412af6dc2f0835` | `outputs/RV6-B-A04-readmission-rollback.json` |
| `c6f5eaa1e14989a97e55dd9d3b12f3a51858e8b5d5e4fcdf00fa2c9082c053b0` | `outputs/RV6-B-A10-surface-classes.json` |
| `1660e79cf05dc7fa65cce49b39b9677680ec674d98795b12c9715fe92d8fed43` | `outputs/RV6-B-A11-machine-classes-r6.json` |
| `2782932f02e3659ccd0e1b498f044c8f57a843e4f12ce3f957e09cd7b466498a` | `outputs/RV6-B-A12-key-subsets-below-threshold.json` |
| `3659b7e803d0ec530a2ebcca2da45a13096c596382bc8301a424e1bf00127919` | `probes/RV6-B-A01-first-contact-selectors.py` |
| `9c60bfedca63a70891985de59324ef01d754f462f04caab2e2b4ec6abff1654a` | `probes/RV6-B-A02-environment-manifest-author.py` |
| `c36fa6b2023aac35144040fdc28d802181059d364fc4d381754dc7dc06bb4bf8` | `probes/RV6-B-A03-generated-statement-rendering.py` |
| `5dec2dcb474d73420eaa0b4121cf70bd6fc363f341b3ab5f204dbaa18f63fb7a` | `probes/RV6-B-A04-readmission-rollback.py` |
| `6bd224f860ebbc84d4b0e144a1fa66359fdf7bf9aecede69cb7eba2ca924a43e` | `probes/RV6-B-A10-surface-classes.py` |
| `1fffa19e005332ccd300dd1aa7af7452d8567b97980d26fc4cc52ba69deeb4e6` | `probes/RV6-B-A11-machine-classes-r6.py` |
| `fc6d5e0ec8febc3bb18a6f85befb3eceb2ab6deef0f7fb4d77a7b92243c66aaf` | `probes/RV6-B-A12-key-subsets-below-threshold.py` |
| `e521de39f078d40f2c0f9bfb08f9e4d3d850426616b0f377b29ecb63820b9dbb` | `probes/compare_reruns.py` |
| `a3f415db0e882abc9e50f70de2e1de7930db395fb73b1ed3481650be511a9aa1` | `probes/rerun_arch_r6.sh` |
| `0e1138a00f15a6041c28c6ca6c357f4737368926d4654cbeec76badc2899bcee` | `probes/rerun_r5_probes.sh` |
| `cebb1874765b9a38200c7c2f54559279985de44d9537fcde90051af9826c30c5` | `rerun/COMPARISON.json` |
| `fe8644dc24c7de7218ee48eefdd067cc8e90e4e365a20d67018cfb7781534fd0` | `rerun/architect-instruments-log.tsv` |
| `680745f625bcddb94cb1f5f425b960586a73169409050235abbddb99f02f2947` | `rerun/review-r5-probes-log.tsv` |
| `fb2e08864dea15a344d74b2fe0ba82f27f39c2abf88dda4da3e84e643a71b893` | `rerun/r5-probe-outputs-that-differ/RV5-B-A05.json` |
| `f18aafd5e6cfaf33d0777cf338ec65d6ffeb364efe3ab5a20d47dd5068560673` | `rerun/r5-probe-outputs-that-differ/RV5-B-A08.json` |
| `c3150ebccf7f190bcc5c5551197183f088e7a24f266d01d802fb26aca74cd3dd` | `rerun/r5-probe-outputs-that-differ/RV5-D-A03.json` |
| `da34c99c9170e6f40e29cfc8e1459995803519e156a592034fa698403118c796` | `rerun/r5-probe-outputs-that-differ/RV5-D-A07.json` |

## Attribution

- **RV6-B-A01 and RV6-B-A04.**
  - Copy FA6's five FA5 substitutions (`SUBS`) and its FA5-prefix loading.
  - A01 re-types FA6's `attacker_world`, `SUB_ADM`, `PLAT` and `evaluator_run` (AR-0015). These follow reviewer B r5
    `lineage_world` (AR-0012).
  - A04 builds R9, B9 and T11 with FA5's own builders.
- **RV6-B-A02.** Built after the architect's ENV6 (AR-0015, helper session), which follows reviewer B r5 `RV5-B-A08`: flags,
  constructor object, signed SHA256SUMS, fetch-by-digest assembly, `op16a` and `op16b` semantics. The code is re-typed.
- **RV6-B-A11.** Adapted from reviewer B r5 `RV5-B-A12-machine-classes.py` (AR-0012): world, machines, adversaries and
  questions. It applies revision-6 rules through P4r6.
- **Re-run scripts.** Adapted from reviewer B r5 `rerun_arch.sh`.
- **Unmodified.** No instrument of the pack or of an earlier review was modified; wrappers call the original functions.
