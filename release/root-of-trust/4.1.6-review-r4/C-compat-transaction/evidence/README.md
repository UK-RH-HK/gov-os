# Evidence — AR-0007 (independent compatibility/transaction review C of RoT-1 revision 4)

Reviewed commit `bca05a7e2c2791126fde1d3d812facdaa45b2e45`. All probes are architecture instruments, not the Governance OS
implementation, run in scratch only. Every child environment has `GOV_*` stripped (only `GOV_KERNEL_CACHE`, into scratch);
`HOME`, `XDG_*` into scratch; `GIT_CONFIG_NOSYSTEM=1`, `PYTHONDONTWRITEBYTECODE=1`. The canonical checkout and the
repository were never written. No forced deletes. Absolute paths in committed outputs are replaced by `<scratch>`,
`<wt>`, `<legacy-bin>`. The real legacy binaries are `gov-4.1.{2,3,4,5}` (SHA-256 recorded in `registers.json` and
`trees-build.json`).

**Independence.** These probes are original to AR-0007 (no code copied from the pack's harnesses or from review r3's
C/D scripts). The registers were re-derived from each binary's `--help`, independently of the architect's P3r3 parser.

## Files

| File | Kind | Establishes |
|---|---|---|
| `c4lib.py` | probe library | child-env hygiene; whole-tree `tree_map` recording every entry (work/`.governance-runtime`/`.git`) by type/mode/size/digest; `git_state`; a faithful re-encoding of the `18` §9 installation-state machine with diagnostics `18` §9 does not examine |
| `register.py` + `registers.json` | executed | each legacy binary's full command register derived from its own `--help` recursion (104/109/115/119 leaf commands) |
| `build_trees.py` + `trees-build.json` | builder | a real legacy 4.1.5 base project (init 4.1.4 → gated update to 4.1.5 → restricted classification added after → realistic prior state) and the revision-4 layouts R4, R4RES, R4APP (variants of the ignore rule and the runtime state) |
| `matrix.py` + `matrix-rows.jsonl` + `matrix-chains.json` + `matrix-summary.json` | executed, 4 real binaries | 10,618 invocations + 168 chains over each register, in positions `--root`, subdirectory (no `--root`), and with env vars; whole-tree before/after; `18` §9 state after |
| `durability.py` + `durability.json` | executed | occupation durability through fresh/shallow clone, `git archive`, `git clean -fdx`, stash/pop, cone/non-cone sparse checkout, `worktree add`, checkout-across-migration, revert, case-collision enumeration, and the untracking idiom on R4 vs R4APP |
| `legacy_regain.py` + `legacy_regain.json` | executed | occupation removal / `git checkout`/`git restore` of pre-migration paths + a legacy CIT targeting `governance/trust/**` (LR-2 / RV3-M6); symlink substitution of an occupation entry; a nested legacy project |
| `subdir_escape.py` + `subdir_escape.json` | executed | held-out attack RV4-C-A01: `init`/`adopt baseline`/`migrate baseline` from a subdirectory escape the occupation and write inside `governance/trust/**` while RoT-1 is `COMPLETE`; the exposure sub-test |
| `REVIEWED-CONTENT-DIGESTS.txt` | manifest | git blob ids of every reviewed pack file at `bca05a7` |

## Running

```sh
S=<fresh scratch>
E="env -i PATH=/usr/bin:/bin HOME=$S/home PYTHONDONTWRITEBYTECODE=1"
$E python3 -B build_trees.py $S/t                     # builds base + R4/R4RES/R4APP; writes $S/t/trees.json
$E python3 -B register.py    $S/reg > registers.json
$E AR7_DISCARD_RUNS=1 python3 -B matrix.py $S/t/trees.json registers.json $S/matrix --workers 18
$E python3 -B durability.py    $S/t/trees.json $S/dur
$E python3 -B legacy_regain.py $S/t/trees.json $S/regain
$E python3 -B subdir_escape.py $S/t/trees.json $S/subesc
```

- The full matrix takes a few minutes with 18 workers (each run copies a fresh tree; `AR7_DISCARD_RUNS=1` reclaims it).
- `matrix.py` writes `matrix-rows.jsonl` **before** running chains, so a chain error never loses the main matrix.

## How claims were tested (architect evidence treated as claims)

- **P3r3** (`../../4.1.6/evidence/P3r3-*`) was read and its register independently re-derived; reproduced for the
  `--root` case; its single gap (no subdirectory invocation) is the RV4-C-H1 class.
- **LR2 / RV3-D-A05-A07 / RV3-C re-runs** were read as claims; the legacy outcomes were reproduced independently
  (`legacy_regain.json`), and the untracking-idiom closure was tested on the retained-line case the architect's tree did
  not exercise (`durability.json` R4APP).
- The RoT-1 install/transaction machinery is architecture-only, so `18`/`20` transaction attacks (foreign journal,
  cross-device, concurrent, crash) were assessed as design (`../02-HELDOUT-ATTACKS.md` A08–A10, `../04-CARRIED-REQUIREMENTS.md`).
