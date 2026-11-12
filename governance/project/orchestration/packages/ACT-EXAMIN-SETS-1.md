# ACT-EXAMIN-SETS-1: the path map declares EXAMIN's set and the proving ground's held-out half (DEC-1130 (3))

**Round 3: a rebuild on the new live map, entries byte-identical (as round 2 was).**
- **Why:** the owner's operator applied ACT-OPERATOR-HOURS-2 this morning; its second commit (`6b8634d2c`: G9 holds only while the night hold is on; `acceptance_exemptions` lists its own commit `8ed7561b68a3`, DEC-1136 (2)) added one entry, two lines (412-413), to `governance/project/path-map.yaml`, so the live map is now `30233a092a4b` (it was `f4029cfb4942`). The round 2 bundle (manifest `e80202922e72...`, reviewed READY) refuses on this map, as it should, and is kept untouched as
  `.gov-runtime/scratch/orchestrator/acts/ACT-EXAMIN-SETS-1.r2-e8020292/` (with its review).
- **What changed:** this ACT's before `f4029cfb4942` to `30233a092a4b`; its after `0ec1d20da86a` to `1fe00f43d8ab`; the hunk's line numbers moved by 2 (`@@ -555,0 +556,19 @@`
  became `@@ -557,0 +558,19 @@`: the insert point is after the two new `acceptance_exemptions` lines); so `list.txt`, the two copies, `apply.sh` (comment lines only: the before hash, "after ACT-OPERATOR-HOURS-2",
  "round 3", `build_r3.py`), the rehearsal log and the manifest. The chain is `30233a092a4b` (live) to `1fe00f43d8ab` (ACT-EXAMIN-SETS-1) to `e4281125cf0e` (ACT-ACCEPTED-REDS-1) to `805bd918d467` (ACT-PATHMAP-EXP-1).
- **What did not:** the entries (the 19 added lines are `tools/entries.yaml` byte for byte and equal round 2's and round 1's added lines: rehearsal C13, C14, C14b; the builder is `tools/insert_entries.py`, unchanged,
  and it reproduces round 2's after copy from round 2's before copy), `apply.sh`'s logic, the `list.txt` shape, the manifest keys, the two checks (each run as written with `bash -c`), class (a), the sets-root step 2,
  the 137 guard cases (the same answers). No bundle touches `tests/acceptance/`, so DEC-1136 (2) adds nothing here.
- **New manifest sha256 `2f814211320cf13edc8cce0eee84bae84a6402cee0b2e6fa6ea8069b52404ba7`** (`sha8` 2f814211). The review of round 2 does not carry to this manifest: a new review is needed; the bundle holds no `review.md` yet.

**Round 2 (history, kept; its hashes are superseded by round 3 above): a rebuild with byte-identical entries on the new map (DEC-1136 (1)); the r1 review's findings carried.**
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
- **By:** a product-spec helper for the CTO, 2026-11-11 (round 2: a helper of the CTO, same day, after the owner's operator applied ACT-W1-01-EXEMPT-3; round 3: a helper of the CTO, 2026-11-12, after ACT-OPERATOR-HOURS-2). Built and rehearsed in a clone and a planted home; **nothing live
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

**Round 3 bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-EXAMIN-SETS-1/` (built in `drafts/examin-sets/acts-r3/ACT-EXAMIN-SETS-1/`). **Manifest sha256
`2f814211320cf13edc8cce0eee84bae84a6402cee0b2e6fa6ea8069b52404ba7`** (`sha8` 2f814211). Every file below is also in its `files` map.

| File | sha256 |
|---|---|
| `before/repo/governance/project/path-map.yaml` (the live map `30233a092a4b`, after ACT-OPERATOR-HOURS-2) | `30233a092a4b80eab66b5cf54232c489ee35b028cda33cb6d6909f09ce704622` |
| `after/repo/governance/project/path-map.yaml` (`1fe00f43d8ab`) | `1fe00f43d8ab564dc8383b859e9a6f93b9d01a40277557c0150364e520e6ff53` |
| `apply.sh` | `c1659eaa2a5c786f8fbacc44949ede8c1bf9f7c0936971ef05c8640173f1652e` |
| `list.txt` | `d14a54f0b1bed03eb858f2954841c58af06c2838fcaba3e776997c076eb6e97c` |
| `rehearsal.log` (the chain's, `drafts/examin-sets/rehearsal.r3.log`, ends `failures: 0`) | `52097d78c545f4f0bfe7b09369fd358124c97a52579376fd256c665914733bf1` |

Earlier rounds stay as they were, superseded, not edited: round 2 (manifest `e80202922e72...`, before `f4029cfb...`, after `0ec1d20d...`) in `acts/ACT-EXAMIN-SETS-1.r2-e8020292/` with its review; round 1
(manifest `97d45565...`, before `fb52ab2d...`, after `b1ffdb0b...`) in `acts/ACT-EXAMIN-SETS-1.r1-97d45565/` and `drafts/examin-sets/ACT-EXAMIN-SETS-1.r1/`.

If the map changes before the apply, `apply.sh check` says `state other` and touches nothing. Rebuild with
`.gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/insert_entries.py <map> --out <after copy>` and `tools/build_r3.py` (it inserts the same block at the end of `evaluation_sets`, refuses if
either entry exists, and checks the result), freeze a new bundle, and review it again.

## 4. The owner's lines
- **Class (a) needs no yes** (the operator applies it after the review's READY and the hash match). If you want to give one:

yes ACT-EXAMIN-SETS-1 2f814211

  Run it BEFORE ACT-ACCEPTED-REDS-1 and ACT-PATHMAP-EXP-1 (REDS's before is this one's after; EXP's before is REDS's after). Before the apply, `apply.sh check` must print
  `state before (sha256 30233a092a4b)`; anything else: stop and tell the CTO. The agent's route is `bash <bundle>/apply.sh apply` from the
  repository root, then its commit as `Role: operator` with `Act: ACT-EXAMIN-SETS-1` (as the rehearsal does). The owner's operator may run
  the same `apply.sh` by hand earlier.
- **Step 2, by hand** (the sets root's map): `bash tools/sets_root_map.sh check`, then `apply`. It keeps the old map as
  `path-map.yaml.pre-ACT-EXAMIN-SETS-1`, inserts the block, parses the result and writes the new map's sha256 beside it.
  `undo` puts the old map back only while the map is as the step left it.
- **Undo of the repository part:** `bash <bundle>/apply.sh undo` (undo ACT-PATHMAP-EXP-1 and ACT-ACCEPTED-REDS-1 first, in that order, if they are on top; byte for byte, only when the map is as this ACT
  left it).

## 5. The rehearsal (round 3: `rehearsal.log`, ends `failures: 0`; 193 checks, the whole chain; `launch-rehearsal.log` is r1's and is unaffected: it does not read the live map)
The chain, in one `--no-hardlinks` clone of `w2/integrate`'s head, all three bundles in order: ACT-EXAMIN-SETS-1 goes by its own `apply.sh` (the plain apply) and is committed in the clone as the agent would (`Role: operator`, `Act:`); ACT-ACCEPTED-REDS-1
then goes by its section 5 commit line (`Role: owner`); ACT-PATHMAP-EXP-1 by its own `apply.sh`, committed as the agent would. `HOME` is planted; a planted sets root with dummy files; the real sets root
and the run folders are never opened or named to a hook. The log holds no head, pid, date or count line of the live tree: the rehearsal ran twice and the two logs are byte for byte equal.

| Step | Result |
|---|---|
| A. preconditions | the clone's and the main tree's map are `30233a092a4b` (EXAMIN's before); REDS's before is EXAMIN's after, EXP's before is REDS's after; the chain is `30233a092a4b` (live) to `1fe00f43d8ab` (ACT-EXAMIN-SETS-1) to `e4281125cf0e` (ACT-ACCEPTED-REDS-1) to `805bd918d467` (ACT-PATHMAP-EXP-1); the clone is clean; DEC-1136 is in the register; no bundle touches `tests/acceptance/` |
| B. **reversed order** | REDS first on `30233a092a4b`: check, apply, undo, verify all exit 3; EXP first on the live map: the same; the map is byte for byte as it was; `git status` empty; no temp file. The round 1 bundles (both ACTs) and the round 2 bundles (all three) refuse the same way (exit 3, nothing touched) |
| C. EXAMIN, the agent's `apply.sh` | state before; verify exit 3; undo says nothing to undo; the 137 guard cases on the map before the entries: 0 failed; the **plain apply**: the map is the frozen after byte for byte, mode 644 kept, `git status` lists only the map, no stray file; apply again changes nothing; the added lines are `entries.yaml` byte for byte and equal r1's and r2's added lines (C13, C14, C14b; hunk headers logged) |
| D. EXAMIN's checks, the guard after, step 2 | **each manifest check as written** with `bash -c`: check 1 (`gov.check.pathmap`) exit 0, check 2 exit 0 (exit 1 on the before map); the same 137 guard cases on the applied map: 0 failed (the same answers); step 2 on the planted sets root's map (equals the applied repository map; `evaluation_sets` names all six sets, `set_fault` None, the measure's gate true for engineer and auditor, false for the orchestrator, `kept_out` names the four folders); undo restores the planted map; EXAMIN committed in the clone; the clone's map is REDS's before; EXP refuses on this map (D16) |
| E to H. REDS (see its package) | plain apply, hunk equal to the bundle's, both checks as written, `validate_entry.py` with the pin's python `-E`: PASS for both entries, the `Role: owner` commit, the pin's ratchet reader counts both |
| H10 to H34. EXP (see its package) | check prints `state before (sha256 e4281125cf0e)`; plain apply; the one added line equals round 2's; both checks as written (check 2 exit 1 on the before map); committed as the agent would; `gov.check.pathmap` exit 0 and **`tests/acceptance/W1-01` green** on the chain's end state |
| I. undo in reverse order | EXP undo, then REDS undo, then EXAMIN undo: the live map `30233a092a4b` byte for byte; REDS's and EXAMIN's undo with EXP on top refuse; EXAMIN's undo with REDS and EXP on top refuses |
| J. refusals (each of the three bundles) | a changed map and a link: check, apply, undo refuse (exit 3); a link at the old fixed temp name is not followed (target untouched); a tampered frozen copy exit 4; map folder not writable exit 5, map untouched, no temp file |
| K. live files | the main tree's map is unchanged (`30233a092a4b`) |

**Section 5 of REDS as written** (the owner's operator's by-hand route) is run on top of this chain in a fresh clone after the manifests were fixed (`tools/run_section5_r3.sh`; its output
`drafts/accepted-reds-1/section5.r3.out` stays beside the logs).

**Not rehearsed:** a real Claude session of either writer (no job was launched), the real sets root's map (never opened; the owner's step 2 has `check` first), and the by-hand commit under the main tree's
own hooks (git's defaults in the clone; the freeze line in REDS's section 5 covers the one known refusal).
