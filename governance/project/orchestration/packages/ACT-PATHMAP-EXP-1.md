# ACT-PATHMAP-EXP-1: the experiments root is in exactly one namespace of the path map (DEC-333, DEC-273)

**One line added to `governance/project/path-map.yaml`, class (b). It frees W2-40 (`DAEO-6ox0`, EXP-002), which the merge queue ejected at 21:38 UTC on 11-11.**

**Round 3: a rebuild on REDS's new after, the one line byte-identical (as round 2 was for the other two).**
- **Why:** the owner's operator applied ACT-OPERATOR-HOURS-2 this morning; its second commit (`6b8634d2c`: G9 holds only while the night hold is on; `acceptance_exemptions` lists its own commit `8ed7561b68a3`, DEC-1136 (2)) added one entry, two lines (412-413), to `governance/project/path-map.yaml`, so the live map is now `30233a092a4b` (it was `f4029cfb4942`). The two ACTs before this one are rebuilt on it (round 3), so this ACT's before moved with them. The round 2 bundle (manifest `9a945c99201d4c2c...`, reviewed READY) refuses on every map of the
  new chain and is kept untouched as `.gov-runtime/scratch/orchestrator/acts/ACT-PATHMAP-EXP-1.r2-9a945c99/` (with its review).
- **What changed:** this ACT's before `5654eca4c139` to `e4281125cf0e`; its after `d50884e3633e` to `805bd918d467`; the hunk's line numbers did **not** move (`@@ -95,0 +96 @@` in both: the line is above the two new
  `acceptance_exemptions` lines); so `list.txt`, the two copies, `apply.sh` (comment lines only: the before hash, and the rebuild hint, which now names `drafts/pathmap-exp-1/insert_exp.py`), the rehearsal log and the manifest. The chain is `30233a092a4b` (live) to `1fe00f43d8ab` (ACT-EXAMIN-SETS-1) to `e4281125cf0e` (ACT-ACCEPTED-REDS-1) to `805bd918d467` (ACT-PATHMAP-EXP-1).
- **What did not:** the one added line (`      - "experiments/**"` after `docs/probes/**` in `doc-records`; the diff of the new after against the new before equals round 2's diff, rehearsal H22, H23), `apply.sh`'s logic, the `list.txt` shape,
  the manifest keys, the two checks (each run as written; check 2 exits 1 on the before map), class (b), the owner's decision inside the yes line (the embedding of experiment records), W2-40's plan. The line was made in rounds 1 and 2 by one
  exact-text replacement typed by hand; round 3 wrote it down as `drafts/pathmap-exp-1/insert_exp.py` (refused unless the anchor line is written once; checks the result), which **reproduces round 2's after copy from round 2's before copy byte for byte**.
- **Rehearsal:** now one clone with the other two (one `--no-hardlinks` clone of `w2/integrate`'s head, all three bundles in order): section 3 below. The round 2 rehearsal's W2-40 merge step (G, H, J of the old table) was **not re-run** in round 3 (the task was the chain; the line, the checks and the
  18-namespace probe are unchanged); say so if it should be.
- **New manifest sha256 `b26fe623d7a685ec7083a224e5f21af4a51503bae4d836d020df32290b73ff5c`** (`sha8` b26fe623). A new review is needed; the bundle holds no `review.md` yet.

## 0. What the owner says

One line, after ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1 are in the map (this ACT's before is the map those two leave, `e4281125cf0e`):

yes ACT-PATHMAP-EXP-1 b26fe623

(`b26fe623` is the first 8 hex of the manifest's sha256 below. Class **(b)**: the operator classifier says `b`, row `path-map`, "a change the row does not allow as (a)": the
line adds a pattern to a namespace, which no `only_added` list of the row covers. It is not a ratchet list, so it is not (O).)

- **Who applies:** the operator agent, from the repository root, after ACT-EXAMIN-SETS-1 and then ACT-ACCEPTED-REDS-1 (REDS is the owner's hand: its commit is `Role: owner`).
  Route: `bash <bundle>/apply.sh check`, then `apply`, then `verify`; the commit is `Role: operator` with `Act: ACT-PATHMAP-EXP-1`, and the ticket trailer the main tree's hooks need.
  `apply.sh` does not commit.
- **What changes:** one line in `namespaces.doc-records.paths`, after `"docs/probes/**"`: `      - "experiments/**"`. Nothing else (the diff is one added line; rehearsal section A).
- **The order:** EXAMIN-SETS-1 (`30233a092a4b` to `1fe00f43d8ab`), ACCEPTED-REDS-1 (`1fe00f43d8ab` to `e4281125cf0e`), then this ACT (`e4281125cf0e` to `805bd918d467`).
  On any other map `apply.sh check` says `state other` and touches nothing.
- **The check line it must print before the apply:** `state before (sha256 e4281125cf0e)`. After the apply: `state applied (sha256 805bd918d467)`, and `verify` exits 0.
  Anything else: stop and tell the CTO.
- **Undo:** `bash <bundle>/apply.sh undo` (byte for byte, only while the map is as this ACT left it; undo this one first if it is on top of the others).
- **Then:** the CTO re-queues W2-40 (head `29753c768def`); its two red tests go green (rehearsed in round 2, section 3 of the round 2 text below; not re-run in round 3).

## 1. Why, and why this line (found in the code, and a correction to the brief)

W2-40's 17 new files: 16 under `experiments/EXP-002/**` (13 result files, `run_hook_limit.py`, `README.md`, `hook-limit-record.md`) and one probe record under `docs/probes/DAEO-6ox0/`
(already in `doc-records`). Nothing in `namespaces` covers `experiments/`, so two tests go red once the branch is in:
`tests/unit/retrieval/test_w2_91_full_embeddings.py::test_every_tracked_path_is_in_one_namespace` and
`tests/acceptance/W1-08/test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace`. `gov.check.pathmap` says `PATH_NO_NAMESPACE` for each of the 16.

**Correction: it is not `research-and-experiments`.** That name is an entry of the top-level `systems:` list (the twenty-two constitutional systems; its `where:` is a documentation list at about line 351).
Both tests, and `gov.check.pathmap`, read only `namespaces:` and each entry's `paths:`. A line added to that `where:` would leave both tests red (no code reads `systems.*.where` for this).
The brief's own words "the `where:` list" named the wrong key: the line goes in a namespace's `paths:`.

**Why `doc-records`.** The root `experiments/` is fixed by decision (DEC-333, DEC-273; the ticket's `allowed_paths` is `experiments/EXP-002/**`), so no folder move is needed.
It must be a namespace that is **not embedded**, and the same line must make no other path match twice. Three homes were weighed:

| Home | Result |
|---|---|
| `doc-records` (`docs/close/**`, `docs/checkpoints/**`, `docs/probes/**`; `embedding_policy: not embedded`; keyword search keeps it) | **chosen.** It already holds the experiment's own probe record; raw run results and a harness are records, not prose to embed; nothing is newly embedded, which is what W2-91's "nothing else moves" rule has held since D-7. One line, no new fields. |
| `docs` (embedded) | not chosen: it would newly embed raw JSON results and a harness script, a retrieval-policy change the owner has not decided. |
| a new namespace `experiments` | the alternative if the owner wants experiments to have a policy of their own (a different `retention`, `sensitivity` or embedding for the evidence records). It needs nine fields and the owner's choice of each, so it is a larger decision than the failure needs. It is not built here; say so and it is a rebuild of this bundle (the same apply.sh, another after copy). |

**One decision for the owner inside the yes line:** the embedding of experiment records. This ACT keeps them out of the embedding index (still found by keyword search), the same as the probes and checkpoints. If you would rather embed the written records (`README.md`, `hook-limit-record.md`) and not the raw results, that needs the new-namespace route with two entries; say so before the yes.

Not changed (and why): `systems.research-and-experiments.where` (documentation only; adding the glob there is optional and a second line, so left alone); the ratchet lists; `tests/acceptance/` (so DEC-1136 (2) adds no exemption entry).

## 2. The files

**Bundle (round 3):** `.gov-runtime/scratch/orchestrator/acts/ACT-PATHMAP-EXP-1/` (built in `drafts/pathmap-exp-1/acts-r3/ACT-PATHMAP-EXP-1/`). **Manifest sha256
`b26fe623d7a685ec7083a224e5f21af4a51503bae4d836d020df32290b73ff5c`** (`sha8` b26fe623). Every file below is also in its `files` map.
The form is ACCEPTED-REDS-1's exactly (same `apply.sh` logic, `list.txt` shape and manifest keys); `claimed_class` is `b`.

| File | sha256 |
|---|---|
| `before/repo/governance/project/path-map.yaml` (ACCEPTED-REDS-1 round 3's `after/` copy, byte for byte: `e4281125cf0e`) | `e4281125cf0ecdd5e8af4edd9c8a2d43b8f4d4693ef05387250384dcb1ac3e47` |
| `after/repo/governance/project/path-map.yaml` (`805bd918d467`: the before plus the one line) | `805bd918d46787b61be2abea8934e5f50619833f5f7eb8bd7ed6c981d649e9b1` |
| `apply.sh` | `092cdd9162b240025c2af8d48573a292abc760967e95d8d967f7cdb0e39d0fa7` |
| `list.txt` | `cd613e4f0cfbcb216e87ac8862858772933f97682036b4bd72d7f51e1d42122a` |
| `rehearsal.log` (the chain's, `drafts/examin-sets/rehearsal.r3.log`, ends `failures: 0`) | `52097d78c545f4f0bfe7b09369fd358124c97a52579376fd256c665914733bf1` |

Round 2's (manifest `9a945c99...`, before `5654eca4c139`, after `d50884e3633e`, its own log `f981a313...`) is in `acts/ACT-PATHMAP-EXP-1.r2-9a945c99/` with its review, untouched.

**The manifest's two checks** (each run as written with `bash -c` in the rehearsal): `PYTHONPATH=src python3 -m gov.check.pathmap` (exit 0), and a `python3 -I -c` that reads the map and asserts:
`doc-records.paths` is exactly the three old patterns plus `experiments/**`; 18 namespaces; `experiments/**` is in exactly one; four sample experiment paths each match exactly one namespace;
`doc-records` is `not embedded`; `accepted_reds` still has its two entries (exit 0; exit 1 on the before map).

**If the order changes** (another path-map ACT lands first, or EXAMIN or REDS is re-built): `apply.sh check` prints `state other`, exit 3, and nothing is touched. Never edit this bundle.
Rebuild the after copy from the then-current map by adding the same one line to `doc-records` (an exact-text replacement that must match once:
`.gov-runtime/scratch/orchestrator/drafts/pathmap-exp-1/insert_exp.py`), copy `apply.sh`, write `list.txt` with the new before and after, run
`.gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/build_r3.py` (it builds all three bundles of the chain; `drafts/pathmap-exp-1/build_manifest.py` is the round 1 and 2 form), rehearse again, and have the new bundle reviewed. The one line is the same in every order.
If W2-40 is re-based and its files move to another root, the ACT is not needed at all.

## 3. The rehearsal (round 3: the chain's `rehearsal.log`, `drafts/examin-sets/rehearsal.r3.log`, ends `failures: 0`, 193 checks; one `--no-hardlinks` clone of `w2/integrate`'s head, the live tree only read; script `drafts/examin-sets/tools/rehearse_r3.sh`)
The log holds no head, pid, date or count line of the live tree (nor a test count or a time); two runs gave byte for byte equal logs. This ACT's steps are B4b, B8, D16, H10 to H34, I0a to I0f, I9 and J (EP):

| Step | Result |
|---|---|
| A. preconditions | the clone's map is `30233a092a4b`; EXP's before is REDS's after (A1b, and `cmp` of the bundle files); the chain is `30233a092a4b` (live) to `1fe00f43d8ab` (ACT-EXAMIN-SETS-1) to `e4281125cf0e` (ACT-ACCEPTED-REDS-1) to `805bd918d467` (ACT-PATHMAP-EXP-1) |
| B. wrong order | on `30233a092a4b` (B4b) and on EXAMIN's after (D16): check, apply, undo, verify all exit 3; the map unchanged, `git status` empty, no temp file; the r2 bundle refuses on the live map (B8) |
| C to H9. the other two | EXAMIN's plain apply and commit; REDS's plain apply and its `Role: owner` commit (their packages) |
| H10 to H21. this ACT | check prints `state before (sha256 e4281125cf0e)`; verify before the apply exits 3; undo with nothing applied says so, exit 0; apply gives `805bd918d467`, mode 644, `git status` lists only the map, no temp file; the map equals the frozen after, byte for byte; verify exit 0; apply again changes nothing; check says `state applied` |
| H22, H23. the line | the diff of the new after against the new before is the one added line `      - "experiments/**"`, equal to round 2's diff (the hunk header is `@@ -95,0 +96 @@` in both: no offset) |
| HX. manifest checks, as written | applied map: check 1 (`gov.check.pathmap`) exit 0, check 2 exit 0; on the before map check 2 exits 1 |
| H30 to H34 | committed in the clone as the agent would (`Role: operator`, `Act: ACT-PATHMAP-EXP-1`); the ratchet still counts both REDS entries; `gov.check.pathmap` exit 0 and `tests/acceptance/W1-01` green on the chain's end state (the ACT touches no file under `tests/acceptance/`, so DEC-1136 (2) adds no entry) |
| I. undo | EXP undo first (REDS's and EXAMIN's undo with it on top refuse), byte for byte back to `e4281125cf0e`; undo again says nothing to undo |
| J. refusals | a changed map and a link: check, apply, undo refuse (exit 3); a link at the old fixed temp name is not followed; a tampered frozen copy exit 4; folder not writable exit 5, map untouched, no temp file |

### Round 2's section 3 (history: round 2's own rehearsal, with W2-40's merge in a clone; its hashes are round 2's: `f4029cfb4942`, `0ec1d20da86a`, `5654eca4c139`, `d50884e3633e`)

| Step | Result |
|---|---|
| A. preconditions | the clone's map is `f4029cfb4942`; my before copy equals REDS's after copy (`cmp`); the diff of before and after is one added line |
| B. wrong order | on `f4029cfb4942`: check, apply, undo, verify all exit 3; the map unchanged, `git status` empty, no temp file |
| C. ACT-EXAMIN-SETS-1 r2 | its own `apply.sh`: check `state before (f4029cfb4942)`, apply to `0ec1d20da86a`, committed in the clone |
| D. ACT-ACCEPTED-REDS-1 r2 | its after copy put in place (`5654eca4c139`), committed in the clone (its section 5 is the owner's, not run) |
| E. this ACT | check prints `state before (sha256 5654eca4c139)`; verify before the apply exits 3; undo with nothing applied says so, exit 0; apply gives `d50884e3633e`, mode 644, `git status` lists only the map, no temp file; the map equals the frozen after, byte for byte; verify exit 0; apply again changes nothing; check says `state applied` |
| F. manifest checks, as written | applied map: both exit 0; undo gives the before copy byte for byte; before map: check 1 exit 0, check 2 exit 1 |
| G. W2-40 merged in the clone (`git merge --no-ff --no-edit 29753c768def`, clone only; 16 `experiments/` files tracked) | **ACT undone: both named tests RED** (`2 failed`; "16 of 4075 tracked paths are in no namespace ... experiments/EXP-002/README.md ..."), `gov.check.pathmap` exit 1 with `PATH_NO_NAMESPACE` |
| H. ACT applied, same merge | **both tests GREEN**; with all of `tests/acceptance/W1-08` and the whole of `test_w2_91_full_embeddings.py`: `127 passed, 114 deselected` (the deselected are `local_only`), exit 0 (through `heavy_slot.sh`, scratch TMPDIR); `gov.check.pathmap` exit 0; an independent walk of all 4075 tracked paths: 0 in none or in two namespaces, the 16 experiment files in `doc-records` only |
| I. undo | back to `5654eca4c139` |
| J. whole `gov check --root <clone>` (each run under 5 minutes) | path-map compliance **RED without, GREEN with**; the other four reds (index freshness, context reproducibility, recovery/rebuild, product traceability) are the same in both runs: a fresh clone has no built index or store |
| K. classifier | `act_class.py` on the bundle: class `b`, row `path-map`, no script hits |

**Where it differs from the real run:** the owner's REDS commit and the operator's commits are plain `git commit` in the clone (no hooks, no `Role:` trailers); the real run takes the main tree's hooks and the
ticket trailer. The map in the real run is the live one after EXAMIN and REDS; the clone got the same bytes by the same files. `gov check` as the brief wrote it (`python3 -m gov check`) does not run
(`gov` has no `__main__`); it was run through `gov.cli.main:main`, the console script's entry. W2-40's real merge by the queue is not rehearsed here (the merge in the clone is a plain merge of the same head); the queue's own gates
(the tickets' tests, the heavy-job slot, the closing checks) run as usual after the ACT. Nothing live was changed, no sets root or run folder was opened, nothing was pushed.
