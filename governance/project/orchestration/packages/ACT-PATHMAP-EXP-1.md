# ACT-PATHMAP-EXP-1: the experiments root is in exactly one namespace of the path map (DEC-333, DEC-273)

**One line added to `governance/project/path-map.yaml`, class (b). It frees W2-40 (`DAEO-6ox0`, EXP-002), which the merge queue ejected at 21:38 UTC on 11-11.**

## 0. What the owner says

One line, after ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1 are in the map (this ACT's before is the map those two leave, `5654eca4c139`):

yes ACT-PATHMAP-EXP-1 9a945c99

(`9a945c99` is the first 8 hex of the manifest's sha256 below. Class **(b)**: the operator classifier says `b`, row `path-map`, "a change the row does not allow as (a)": the
line adds a pattern to a namespace, which no `only_added` list of the row covers. It is not a ratchet list, so it is not (O).)

- **Who applies:** the operator agent, from the repository root, after ACT-EXAMIN-SETS-1 and then ACT-ACCEPTED-REDS-1 (REDS is the owner's hand: its commit is `Role: owner`).
  Route: `bash <bundle>/apply.sh check`, then `apply`, then `verify`; the commit is `Role: operator` with `Act: ACT-PATHMAP-EXP-1`, and the ticket trailer the main tree's hooks need.
  `apply.sh` does not commit.
- **What changes:** one line in `namespaces.doc-records.paths`, after `"docs/probes/**"`: `      - "experiments/**"`. Nothing else (the diff is one added line; rehearsal section A).
- **The order:** EXAMIN-SETS-1 (`f4029cfb4942` to `0ec1d20da86a`), ACCEPTED-REDS-1 (`0ec1d20da86a` to `5654eca4c139`), then this ACT (`5654eca4c139` to `d50884e3633e`).
  On any other map `apply.sh check` says `state other` and touches nothing.
- **The check line it must print before the apply:** `state before (sha256 5654eca4c139)`. After the apply: `state applied (sha256 d50884e3633e)`, and `verify` exits 0.
  Anything else: stop and tell the CTO.
- **Undo:** `bash <bundle>/apply.sh undo` (byte for byte, only while the map is as this ACT left it; undo this one first if it is on top of the others).
- **Then:** the CTO re-queues W2-40 (head `29753c768def`); its two red tests go green (rehearsed below).

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

**Bundle:** `.gov-runtime/scratch/orchestrator/drafts/pathmap-exp-1/ACT-PATHMAP-EXP-1/`. **Manifest sha256
`9a945c99201d4c2c49cbd522c38b3ebee5b2fa0c09dbb5f9e62f852721b6e93c`** (`sha8` 9a945c99). Every file below is also in its `files` map.
The form is ACCEPTED-REDS-1's exactly (same `apply.sh` logic, `list.txt` shape and manifest keys); `claimed_class` is `b`.

| File | sha256 |
|---|---|
| `before/repo/governance/project/path-map.yaml` (ACCEPTED-REDS-1's `after/` copy, byte for byte: `5654eca4c139`) | `5654eca4c139be0e2f8457593a685fcd9d747657e952215e3c46bcac45998211` |
| `after/repo/governance/project/path-map.yaml` (`d50884e3633e`: the before plus the one line) | `d50884e3633e6e778626a17a0cae62f37778ff7f1903b2a557ad7920e9bbbb4d` |
| `apply.sh` | `d51e8749d3ab80a0bf5194cb81027bbe28fd2ea0515473d4354d72cda5b45d6e` |
| `list.txt` | `ee4fc76d9483104877df4c5540eefb2ae4750f130a3f328ac4b66f9b183d79c2` |
| `rehearsal.log` (ends `checks: 21; failures: 0`) | `f981a313350fe4234358c0f02dbf3fc5edaa2ff25cd666d1a18fd3e352c85877` |

**The manifest's two checks** (each run as written with `bash -c` in the rehearsal): `PYTHONPATH=src python3 -m gov.check.pathmap` (exit 0), and a `python3 -I -c` that reads the map and asserts:
`doc-records.paths` is exactly the three old patterns plus `experiments/**`; 18 namespaces; `experiments/**` is in exactly one; four sample experiment paths each match exactly one namespace;
`doc-records` is `not embedded`; `accepted_reds` still has its two entries (exit 0; exit 1 on the before map).

**If the order changes** (another path-map ACT lands first, or EXAMIN or REDS is re-built): `apply.sh check` prints `state other`, exit 3, and nothing is touched. Never edit this bundle.
Rebuild the after copy from the then-current map by adding the same one line to `doc-records` (an exact-text replacement that must match once, in the style of
`.gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/insert_entries.py`), copy `apply.sh`, write `list.txt` with the new before and after, run
`.gov-runtime/scratch/orchestrator/drafts/pathmap-exp-1/build_manifest.py`, rehearse again, and have the new bundle reviewed. The one line is the same in every order.
If W2-40 is re-based and its files move to another root, the ACT is not needed at all.

## 3. The rehearsal (`rehearsal.log`; clone of `w2/integrate`, `--no-hardlinks`; the live tree only read; scripts `rehearse-1.sh`, `rehearse-2.sh` beside the bundle)

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
