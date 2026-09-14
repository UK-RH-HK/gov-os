# Evidence — AR-0003 (independent compatibility/transaction review C of RoT-1 revision 3)

Reviewed commit `ca77a431418bd6b349f465aa2521ca43bccfd5a6`. All probes are architecture instruments, run in scratch
only; `GOV_*` stripped from every child; `GOV_KERNEL_CACHE`, `HOME`, `XDG_*` pointed into scratch; the canonical
checkout and the repository are never written. Absolute scratch paths in the JSON are replaced by `<scratch>`.
The four real legacy binaries used are `gov-4.1.{2,3,4,5}` (SHA-256 recorded in `lib.py`/the orchestrator state).

| File | Kind | Establishes |
|---|---|---|
| `lib.py` | probe library | child-env hygiene; whole-tree `file_map` recording entry TYPE (file/dir/link) + digest; git-state capture |
| `build_base.py` | builder | real 4.1.5 base project (init 4.1.4 → gated update to 4.1.5 → restricted classification added after), then the RoT-1 rev3 legacy-path-occupation layout (`08` §2, `26` §2) committed as the migration commit on top of legacy history |
| `run_destructive.py` + `destructive.json` | executed, 4 real binaries | 84 destructive/state-changing invocations on L3 (update rollback/apply-older, init --force, reinstall, adopt/migrate baseline+rollback, recover, cit/tools/plugins, override, rebuild), whole-tree + `governance/trust` + git before/after |
| `durability.py` + `durability.json` | executed | occupation durability through fresh clone, `git archive`, checkout across the migration commit, case-collision enumeration, `git clean -fdx`, non-cone sparse-checkout omitting occupation, `git revert` of the migration commit; each followed by real legacy remedies |
| `occ_removal.py` + `occ_removal.json` | executed | partial occupation removal (the 3 inscrutable sentinel files) + legacy `init --force`; governance/trust mutation + restricted-exposure check |
| `full_removal_and_merge.py` + `full_removal_and_merge.json` | executed | (A) full occupation removal incl the `framework.lock` directory + legacy `init --force`, governance/trust kept; (B) divergent dir/file merge (legacy branch edits `governance/kernel/` dir vs RoT-1 file) |
| `REVIEWED-CONTENT-DIGESTS.txt` | manifest | git blob ids of every reviewed pack file at `ca77a43` |

## Running
```sh
S=<fresh scratch>
python3 build_base.py $S           # prints base + L3 paths
python3 run_destructive.py $S $S/L3 > destructive.json
python3 durability.py $S/d $S/L3 > durability.json
python3 occ_removal.py $S/o $S/L3 > occ_removal.json
python3 full_removal_and_merge.py $S/f $S/base $S/L3 > full_removal_and_merge.json
```
The architect's `P3r3`, `P1r3`, `P4r3`, `G1` and `CSI` were treated as claims. `run_destructive.py` reproduces the
LP-1 no-write property independently on a hand-built layout; `durability.py`/`occ_removal.py`/`full_removal_and_merge.py`
attack the layout's durability, which `P3r3` did not.
