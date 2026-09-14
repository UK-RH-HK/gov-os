# Evidence — AR-0013 (independent compatibility/transaction review C of RoT-1 revision 5)

Reviewed commit `cdb4e14009bba60bea9b805563c1b60e84f30b4b`. All probes are architecture instruments, not the Governance OS
implementation, run in scratch only. Every child environment is constructed (never inherited): `GOV_*` absent except
`GOV_KERNEL_CACHE` into scratch (and, in the `P-ENV` matrix rows, the one `GOV_*` variable under test, set explicitly as
the object of the test); `HOME`, `XDG_*` into scratch; `GIT_CONFIG_NOSYSTEM=1`, `GIT_OPTIONAL_LOCKS=0`,
`PYTHONDONTWRITEBYTECODE=1`, `core.hooksPath=/dev/null`. The canonical checkout and every other worktree were never
written. No forced deletes. Absolute paths in committed outputs are replaced by `<scratch>`, `<wt>`, `<legacy-bin>`. The
real legacy binaries are `gov-4.1.{2,3,4,5}` (SHA-256 in `REVIEWED-CONTENT-DIGESTS.txt`).

**Independence.** Every probe is original to AR-0013. The installation-state predicate `c5lib.state_r5` is encoded from
the text of `18` §9/§9.1/§9.2 at `cdb4e14`; it does not import the architect's `ST5-installation-state-r5.py` or review r4
C's `c4lib.installation_state`. The registers are re-derived from each binary's `--help` and from its own source,
independently of the architect's P3r3 parser. Prior probes (review r4 C/D, architect ST5, P3r3) are copied only for
reproduction, run unmodified, with attribution.

## Files

| File | Kind | Establishes |
|---|---|---|
| `probes/c5lib.py` | library | child-env hygiene; whole-tree snapshot; `state_r5` (`18` §9/§9.1 encoded from the text); `kernel_tampered` (`18` §6.1 vs `RCS(D)`); `discover_r5` (`18` §9.2); nested-marker and journal-honour predicates |
| `probes/register5.py` + `outputs/registers5.json` | executed | each binary's register from `--help` **and** from source, cross-checked (104/109/115/119 leaves) |
| `probes/build5.py` + `outputs/build5-facts.json` | builder | the real 4.1.5 base project and the revision-5 trees R5/R5RES/R5NOSURG/R5V/L0 |
| `probes/gitops5.py` + `outputs/gitops.json` | executed, real Git | 18 trees from ordinary Git operations (clone/shallow/partial/sparse/archive/clean/stash/worktree/checkout/restore/untracking idiom/global excludes/info-exclude/autocrlf/text=auto) and their `18` §9.1 state |
| `probes/matrix5.py` + `outputs/matrix5-summary.json` + `outputs/matrix5-writing-rows-rot1-layouts.json` | executed, 4 real binaries | 30,165 rows + 1,335 `--root` rows over the mutating families + a control sample, in positions P-ROOT/P-CWD/P-VEND/P-ENV/P-GIT; whole-tree before/after; `18` §9.1 state; decisive properties (LP-1r, R2-H4 class, classification loss, Git-op elevation) |
| `probes/admit_tx.py` + `outputs/admit_tx.json` | model | transactional properties of the pack's `gov-admit` reference executor (crash-after-install, re-run move-aside, rollback record survival, concurrent admissions) |
| `probes/repro_prior.sh` | runner | re-runs the prior decisive probes against revision 5 |
| `reproduction/REPRODUCTION.json` | executed | byte-comparison of the reproduced prior probes with their committed outputs |
| `REVIEWED-CONTENT-DIGESTS.txt` | manifest | git blob ids of every reviewed pack, D-0008, ARCH-0002 and review-r4 file at `cdb4e14`; legacy-binary SHA-256 |

## Running

```sh
S=<fresh scratch>;  W=<this worktree>;  L=<legacy-bin dir>
E="env -i PATH=/usr/bin:/bin HOME=$S/home PYTHONDONTWRITEBYTECODE=1 AR13_SCRATCH=$S AR13_WT=$W AR13_LEGACY_BIN=$L"
$E python3 -B probes/register5.py $S/reg       > outputs/registers5.json
$E python3 -B probes/build5.py    $S/t                                   # writes $S/t/trees.json
$E python3 -B probes/gitops5.py   $S/t/trees.json $S/gitops
$E python3 -B probes/matrix5.py   $S/t/trees.json outputs/registers5.json $S/gitops/gitops-trees.json $S/matrix5 --workers 16 --focus
$E python3 -B probes/admit_tx.py  $S/admit
AR13_SCRATCH=$S AR13_WT=$W AR13_LEGACY_BIN=$L bash probes/repro_prior.sh  # reproduction of prior probes
```

- `matrix5.py --focus` restricts the register to the mutating families plus a control sample; the full-register no-write
  property is corroborated by the reproduced review r4 C matrix (10,618 invocations) and P3r3 (2,085 jobs).
- Each matrix row copies a fresh tree and deletes it after snapshotting, so disk use stays bounded.

## How claims were tested (architect evidence treated as claims)

- **ST5** (`../../../4.1.6/evidence/r5/ST5-*`), **P3r3**, **review r4 C/D** probes were re-run unmodified against revision
  5 and compared with their committed outputs (`reproduction/REPRODUCTION.json`): byte-identical except run-specific
  timestamps and record ids.
- The revision-5 installation-state claim (`18` §9.1 closes the trust PPS) was tested with an **independent** predicate
  (`c5lib.state_r5`) over 30,165 rows; the R2-H4 class property held with 0 violations.
- The RoT-1 install/transaction machinery and `gov-admit` are architecture-only, so `18`/`20`/`31` transaction attacks
  were assessed as design and against the pack's reference executor (`02-HELDOUT-ATTACKS.md` A08–A11,
  `04-CARRIED-REQUIREMENTS.md`).
