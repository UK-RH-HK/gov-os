# ACT-EXAMIN-SETS-1: the path map declares EXAMIN's set and the proving ground's held-out half (DEC-1130 (3))

**Round 2: a rebuild with byte-identical entries on the new map (DEC-1136 (1)); the r1 review's findings carried.**
ACT-W1-01-EXEMPT-3 was applied by the owner's operator (`7b5c3cb94fd9`, `Role: owner`; two lines in `acceptance_exemptions`), so the live
map is now `f4029cfb4942` (it was `fb52ab2dc756`). The r1 bundle (reviewed READY, manifest `97d45565...`) refuses on this map, as it
should, and is kept untouched as `ACT-EXAMIN-SETS-1.r1/` beside this file and under `acts/`. Round 2 is the same two entries, inserted by the
same builder (`tools/insert_entries.py`, `tools/entries.yaml`): the added lines are `entries.yaml` byte for byte and equal the r1 bundle's
added lines (rehearsal C13, C14). Only the before copy, the after copy, `list.txt`, `apply.sh` and the rehearsal differ.
**Neither this ACT nor ACT-ACCEPTED-REDS-1 touches `tests/acceptance/`** (each changes only `governance/project/path-map.yaml`), so
DEC-1136 (2) (an ACT whose commit changes `tests/acceptance/` carries its own `acceptance_exemptions` entry) adds nothing to either.
**The r1 review's findings, carried:** F1 each manifest check is run as written with `bash -c` (rehearsal D); F2 the plain apply is
rehearsed (C5), and `apply.sh` makes no backup file at all now; F3 the rebuild hint names the tool by its repository path; F4 the temp file is
made by `mktemp` in the map's folder (a link planted at the old fixed name is not followed: rehearsal chain J8). From ACT-W1-01-EXEMPT-3's
review: the log holds no head, pid, date or count line of the live tree (a re-run is byte for byte equal), and `apply.sh`'s comment names
a tool that exists. **Chain on the new map:** this ACT `f4029cfb` to `0ec1d20d`; ACT-ACCEPTED-REDS-1 (round 2) `0ec1d20d` to `5654eca4`.

- **For:** the owner's operator (class (a), applied after an independent review says READY), and the owner's own hand for
  the sets root's map (step 2 below).
- **By:** a product-spec helper for the CTO, 2026-11-11 (round 2: a helper of the CTO, same day, after the owner's operator applied ACT-W1-01-EXEMPT-3). Built and rehearsed in a clone and a planted home; **nothing live
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

**Round 2 bundle:** `.gov-runtime/scratch/orchestrator/drafts/examin-sets/acts-r2/ACT-EXAMIN-SETS-1/`. **Manifest sha256
`e80202922e72b3e55767efceef315b8ead863de443fb4036aab24cb6f9e8674f`** (`sha8` e8020292). Every file below is also in its `files` map.

| File | sha256 |
|---|---|
| `before/repo/governance/project/path-map.yaml` (the live map `f4029cfb4942`, after ACT-W1-01-EXEMPT-3) | `f4029cfb49428708a7c7f9ca754bcd50a1c610ccc22966d09c4c581f1abbd971` |
| `after/repo/governance/project/path-map.yaml` (`0ec1d20da86a`) | `0ec1d20da86a4bdb0f38affe6bd76e86185af3152478ea6422e764442df8645d` |
| `apply.sh` | `3214474e96aa74cdaf6cbf05b93e4cd3db13db700aa932c5d7760abaf21284a0` |
| `list.txt` | `c29875294c52d2ccafac1b5064a408baa15b46a790a957153ab5e51818af2172` |
| `rehearsal.log` (the chain's, `drafts/examin-sets/rehearsal.r2.log`, ends `failures: 0`) | `69e57ee8b53e34a3de64f638f5ffaa7f59f91a88e99702632e5880e422e5bbc9` |

The r1 bundle (manifest `97d45565...`, before `fb52ab2d...`, after `b1ffdb0b...`) stays in `acts/ACT-EXAMIN-SETS-1/` with its review, and as
`drafts/examin-sets/ACT-EXAMIN-SETS-1.r1/`; it is superseded, not edited.

If the map changes before the apply, `apply.sh check` says `state other` and touches nothing. Rebuild with
`.gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/insert_entries.py <map> --out <after copy>` and `tools/build_r2.py` (it inserts the same block at the end of `evaluation_sets`, refuses if
either entry exists, and checks the result), freeze a new bundle, and review it again.

## 4. The owner's lines
- **Class (a) needs no yes** (the operator applies it after the review's READY and the hash match). If you want to give one:

yes ACT-EXAMIN-SETS-1 e8020292

  Run it BEFORE ACT-ACCEPTED-REDS-1 (that one's before is this one's after). Before the apply, `apply.sh check` must print
  `state before (sha256 f4029cfb4942)`; anything else: stop and tell the CTO. The agent's route is `bash <bundle>/apply.sh apply` from the
  repository root, then its commit as `Role: operator` with `Act: ACT-EXAMIN-SETS-1` (as the rehearsal does). The owner's operator may run
  the same `apply.sh` by hand earlier.
- **Step 2, by hand** (the sets root's map): `bash tools/sets_root_map.sh check`, then `apply`. It keeps the old map as
  `path-map.yaml.pre-ACT-EXAMIN-SETS-1`, inserts the block, parses the result and writes the new map's sha256 beside it.
  `undo` puts the old map back only while the map is as the step left it.
- **Undo of the repository part:** `bash <bundle>/apply.sh undo` (undo ACT-ACCEPTED-REDS-1 first if it is on top; byte for byte, only when the map is as this ACT
  left it).

## 5. The rehearsal (round 2: `rehearsal.log`, ends `failures: 0`; 124 checks; `launch-rehearsal.log` is r1's and is unaffected: it does not read the live map)
The chain, in **one** `--no-hardlinks` clone of `w2/integrate` (`tools/rehearse_r2.sh`; `HOME` planted; a planted sets root with dummy files;
the real sets root and the run folders are never opened or named to a hook). EXAMIN goes by its own `apply.sh` (the plain apply) and is
committed in the clone as the agent would (`Role: operator`, `Act:`); ACT-ACCEPTED-REDS-1 then goes by its section 5 commit line
(`Role: owner`). The log holds no head, pid, date or count line of the live tree: the rehearsal ran twice and the two logs are byte for byte
equal.

| Step | Result |
|---|---|
| A. preconditions | the clone's and the main tree's map are `f4029cfb4942` (EXAMIN's before); REDS's before is EXAMIN's after; the chain hashes are `0ec1d20d` and `5654eca4`; the clone is clean; DEC-1136 is in the register; neither bundle touches `tests/acceptance/` |
| B. **reversed order** | REDS first on `f4029cfb`: check, apply, undo, verify all exit 3; the map is byte for byte as it was; `git status` empty; no temp file. The r1 bundles of both ACTs refuse the same way (exit 3, nothing touched) |
| C. EXAMIN, the agent's `apply.sh` | state before; verify exit 3; undo says nothing to undo; the 137 guard cases on the map before the entries: 0 failed; the **plain apply**: the map is the frozen after byte for byte, mode 644 kept, `git status` lists only the map, no stray file; apply again changes nothing; the added lines are `entries.yaml` byte for byte and equal r1's added lines |
| D. EXAMIN's checks, the guard after, step 2 | **each manifest check as written** with `bash -c`: check 1 exit 0, check 2 exit 0 (exit 1 on the before map); the same 137 guard cases on the applied map: 0 failed (the same answers); step 2 on the planted sets root's map (equals the applied repository map; `evaluation_sets` names all six sets, `set_fault` None, the measure's gate true for engineer and auditor, false for the orchestrator, `kept_out` names the four folders); undo restores the planted map; EXAMIN committed in the clone; the clone's map is REDS's before |
| E to H. REDS (see its package) | plain apply, hunk equal to the bundle's, both checks as written, `validate_entry.py` with the pin's python `-E`: PASS for both entries, the `Role: owner` commit, the pin's ratchet reader counts both |
| I. undo in reverse order | REDS undo, then EXAMIN undo: the live map `f4029cfb` byte for byte; EXAMIN's undo with REDS on top refuses |
| J. refusals (each bundle) | a changed map and a link: check, apply, undo refuse (exit 3); a link at the old fixed temp name is not followed (target untouched); a tampered frozen copy exit 4; map folder not writable exit 5, map untouched, no temp file |
| K. live files | the main tree's map is unchanged (`f4029cfb4942`) |

**Section 5 of REDS as written** (the owner's operator's by-hand route) is run on top of this chain in a fresh clone after the manifests were
fixed (`tools/run_section5_r2.sh`; its output `drafts/accepted-reds-1/section5.r2.out` stays beside the logs).

**Not rehearsed:** a real Claude session of either writer (no job was launched), the real sets root's map (never opened; the owner's step 2
has `check` first), and the by-hand commit under the main tree's own hooks (git's defaults in the clone; the freeze line in REDS's section 5
covers the one known refusal).
