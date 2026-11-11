# ACT-EXAMIN-SETS-1: the path map declares EXAMIN's set and the proving ground's held-out half (DEC-1130 (3))

- **For:** the owner's operator (class (a), applied after an independent review says READY), and the owner's own hand for
  the sets root's map (step 2 below).
- **By:** a product-spec helper for the CTO, 2026-11-11. Built and rehearsed in a clone and a planted home; **nothing live
  was changed, and nothing under the real sets root or the run folders was opened.**
- **Sources:** DEC-1130 (3); DEC-1101 (2)-(3); DEC-1082 (3); DEC-1097 (2); DEC-957; tickets W2-94 (`DAEO-g87r`) and W2-93
  (`DAEO-6y0x`); ACT-SETS-GLOBS-1; ACT-MSET-3 section 10 (the same two-map entry for `memory-verdict-2`);
  `governance/project/operator/class-rules.yaml` (row `path-map`).

## 1. What changes
Two entries at the end of `evaluation_sets` in `governance/project/path-map.yaml`, and nothing else:

| Set | visible | hidden | measures (roles) |
|---|---|---|---|
| `examin` | `fixtures/evaluation/examin/visible/**` | `fixtures/evaluation/examin/hidden/**` | engineer, research, product-spec, independent-test-designer, independent-auditor (as `memory-verdict-2`) |
| `adoption-proving-ground` | `tests/acceptance/W2-81/questions/**` | `fixtures/evaluation/adoption-proving-ground/hidden/**` | the same five |

The tickets' wording says "by tickets"; the four entries made since DEC-1082 measure by role, so these do too (choice C7
in `FOR-THE-OWNER.md`). The sets themselves live under the sets root (`~/gov-os-eval/fixtures/evaluation/<set>/`), never
in a tree, and the launch script delivers into their `hidden/` folder.

## 2. What it does and does not do (found in the code, rehearsed)
- **The guard already refuses the hidden halves.** `sets_root_hidden` has `fixtures/evaluation/*/hidden/**` and
  `fixtures/evaluation/*/XCHECK-r*.md` (ACT-SETS-GLOBS-1). Under the sets root **and in every tree** they are refused to the
  six roles and the orchestrator, for any set name. The rehearsal ran 137 cases before and after: **the same 137 answers.**
  So the entries close no guard gap. They make the sets declared.
- **What the declaration is for.** `gov.retrieval.measure examin ...` refuses a set that is not declared; it reads the
  declaration from the **sets root's own map** (`<sets root>/governance/project/path-map.yaml`), not from the repository. That
  copy is the owner's by hand (class O), so step 2 below adds the same block there, as ACT-MSET-3 section 10 did. The
  repository entry keeps the two maps equal (the rehearsal checks the planted pair are byte-equal) and lets `check_sets`
  and the role-based refusal see the sets.
- **The store already keeps the folders out.** `fixtures/evaluation/**` is the namespace `evaluation-fixtures`
  (`lexical_policy: not indexed`, `embedding_policy: not embedded`). `kept_out` named all four folders (hidden and visible
  of each set) as kept out; no change.
- **The proving ground's visible half is W2-81's own questions folder** and stays readable and indexed as today.

## 3. Class and the files
**Class (a): tightening only.** Row `path-map` of `class-rules.yaml`: "a new `evaluation_sets` entry with its hidden globs"
is `only_added` and `new_entry_needs: hidden` holds. No script hit (`commands: []`, apply.sh only copies the frozen file).
The sets root's map is class O (row `walled-sessions`: `~/gov-os-eval/**`): the owner's hand, not in the bundle.

| File (`.gov-runtime/scratch/orchestrator/drafts/examin-sets/ACT-EXAMIN-SETS-1/`) | sha256 |
|---|---|
| `before/repo/governance/project/path-map.yaml` (the map `fb52ab2dc756`) | `fb52ab2dc7568d24234b755abc7fd6ad7b21743ca3d01b572ef7e9dc40fc2d95` |
| `after/repo/governance/project/path-map.yaml` (`b1ffdb0b7b3e`) | `b1ffdb0b7b3e2fb25f7a5ef8e7417a0710197cc4dbd2efac73a08a3ad6a61878` |
| `apply.sh`, `list.txt`, `manifest.json`, `rehearsal.log` | in `manifest.json` (`files`); the bundle's `sha8` is the first 8 digits of `manifest.json`'s sha256 |

If the map changes before the apply, `apply.sh check` says `state other` and touches nothing. Rebuild with
`tools/insert_entries.py <map> --out <after copy>` (it inserts the same block at the end of `evaluation_sets`, refuses if
either entry exists, and checks the result), freeze a new bundle, and review it again.

## 4. The owner's lines
- **Class (a) needs no yes** (the operator applies it after the review's READY and the hash match). If you want to give one:
  `yes ACT-EXAMIN-SETS-1 <sha8>`.
- **Step 2, by hand** (the sets root's map): `bash tools/sets_root_map.sh check`, then `apply`. It keeps the old map as
  `path-map.yaml.pre-ACT-EXAMIN-SETS-1`, inserts the block, parses the result and writes the new map's sha256 beside it.
  `undo` puts the old map back only while the map is as the step left it.
- **Undo of the repository part:** `bash ACT-EXAMIN-SETS-1/apply.sh undo` (byte for byte, only when the map is as this ACT
  left it).

## 5. The rehearsal (`rehearsal.log`, ends `failures: 0`; 31 checks; `launch-rehearsal.log`, ends `failures: 0`)
A `--no-hardlinks` clone of `w2/integrate` at `625aa084fa02`; a planted home whose `gov-os-eval` holds dummy files. Every
hook run had `HOME` set to the planted home.

| Step | Result |
|---|---|
| A. `apply.sh` check, verify, undo before the apply | state before; verify refused (exit 3); undo says nothing to undo |
| B. 137 guard cases before the entries (engineer, research, product-spec, test designer, auditor, CTO, lead; Read, Grep, Glob, Bash `cat`, Write; hidden folder, `hidden/visible`, `XCHECK-r1.md`, the visible folder, in the sets root and in a tree, the harness's own `--sets-root <root>` line) | 0 failed |
| C. apply with a backup | frozen after, byte for byte; the backup is the original; apply again changes nothing |
| D. `PYTHONPATH=src python3 -m gov.check.pathmap` | exit 0; the map differs from the original by the two entries only |
| E. the same 137 cases on the applied map | 0 failed (the same answers: the planted hidden path is refused to the engineer, the CTO and the test designer, as before) |
| F. step 2 on a planted sets root's map | applied; the planted map equals the repository's; `evaluation_sets` names all six sets, `set_fault` is None for each, the measure's gate `_measured` is true for engineer and auditor and false for the orchestrator; `kept_out` names the four folders `evaluation-fixtures`; undo refused after a later change, then restores byte for byte |
| G. a map changed after the freeze | `check` and `undo` refuse; undo from the applied state restores the original |
| H. live files | the main tree's map is unchanged (`fb52ab2dc756`) |

**Not rehearsed:** a real Claude session of either writer (no job was launched; the launch script's `--dry` built both
walls and trees on a planted sets root), and the real sets root's map (never opened; the owner's step 2 has `check`
first).
