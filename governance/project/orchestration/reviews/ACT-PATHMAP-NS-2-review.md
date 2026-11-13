# The review of ACT-PATHMAP-NS-2: the path-map namespace for governance/project/indep-briefs/**

- Brief: `.gov-runtime/scratch/orchestrator/briefs/ACT-PATHMAP-NS-2-review.md`; manifest `b19855849e1e…`; reviewer (Opus, max, launched under W2-20) log `/home/usain/gov-os-worktrees/W2-20/.gov-runtime/scratch/lead/log/ACT-PATHMAP-NS-2-review.json`
- verdict.py: READY (F1 in scope, other: the five briefs become searchable by every session after the commit; F2 out of scope: a hand commit during an agent ACT is refused by the freeze; wait for the agent, then commit).

The sandbox check passed, the ps check found nothing, and the verdict is **pass**: the ACT is ready for the owner's yes. Every hash matches. The change is exactly the two lines. My own re-run at the main tree's current head behaves as the package says. There are two findings and neither blocks.

**Sandbox check (Step 0):**
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r30l','w').write('x')"` failed with `OSError: [Errno 30] Read-only file system` (exit 1). Nothing was written.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (blob 1ae28402a109, exit 0), and `git update-index --refresh` worked (exit 0). The check passed, so the review went ahead.

**ps check:** `ps -eo pid,ppid,user,args | grep -iE "[o]llama|[l]lama-server"` printed nothing. I started no model, embedder or reranker.

- **task:** DAEO-r30l, the independent read-only review of ACT-PATHMAP-NS-2 (KPI `act-pathmap-ns-2`), before the owner's yes (class (b), by hand).
- **status:** DONE. Verdict **pass**, with no blocking finding. F1 is in scope with consequence "other"; F2 is out of scope.
- **work_completed:**
  - Read the package, the bundle and the precedent (ACT-PATHMAP-NS-1).
  - Read `class-rules.yaml` and how the guard hook uses the map.
  - Read `gov.check.pathmap` and the indexer: `gov.secrets.indexable`, `lexical.py` and `semantic.py`.
  - Read the walls' template, `kinds.yaml` and `tree-exclude.txt`.
  - Read DEC-1101, DEC-1112, DEC-1113 and DECIDED-NOT-DONE rows 76 and 87.
  - Recomputed every hash.
  - Re-ran the rehearsal in a fresh clone of today's head under my own TMPDIR, including the operator's commit line and `git revert`.
  - Ran the operator's `act_class.py` on the bundle, which only reads.
- **files_changed:** none. The live map and the bundle were only read. My clone and bundle copy under the session TMPDIR were removed. Step 0 (b) wrote one blob into the shared object store, as that step requires.
- **evidence:**
  - All seven hashes match the manifest and the package.
  - The live map equals `before/` (`cmp` exit 0).
  - Applying the bundle's patch to `before/` gives `after/` byte for byte.
  - Re-run at 5f5998bab0d6, before the change: 5 × PATH_NO_NAMESPACE, the five briefs and nothing else.
  - After the change: `gov.check.pathmap` exits 0 with no findings; of 3882 tracked paths, 0 match no namespace and 0 match several.
  - `act_class.py` returns `{"class": "b", "row": "path-map", "hits": []}`.
  - TMPDIR at the end: `du -sh` 48K, `du -s --inodes` 14. While the clone existed it peaked at 55M and 4551 inodes.
- **tests:** the file run was `tests/acceptance/W1-08/test_w1_08_path_map.py`, in the clone with the map applied.
  - Run through `heavy_slot.sh` with HOME set to an empty folder, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, and PYTHONPATH set to the clone's `src`.
  - Run 1, with `-m "not local_only" -k "not real and not green_here and not time_limit"`: 12 passed, 22 deselected.
  - Run 2, with the `-k` part only: **28 passed, 6 deselected**. This is the rehearsal's own count. `test_every_tracked_path_matches_exactly_one_namespace` and both schema-validation cases on the applied map were among the passes.
  - The `-k` part matches none of the file's 34 tests (a collect-only run selected 0).
  - `-m "not local_only"` left out 16 schema cases, which start no model and were run in run 2.
  - The 6 left out in both runs are deselected by the repository's own collection rules.
  - No real model was used, and not the full suite.
- **discoveries:**
  1. Today's head (5f5998bab0d6) is two commits past the rehearsal's head (baac0b2c2f61). The three files added since then each match exactly one namespace. So the package's 3879 tracked paths are now 3882, with the same result.
  2. The guard never reads `namespaces`. Anywhere in `src/gov`, `permitted_roles`, `sensitivity` and `export_policy` are only checked against the schema, never enforced.
  3. The launch script's usage lines place future audit briefs directly under `governance/project/indep-briefs/` (`writer.md`, `checker.md`, `auditor.md`). The folder-wide glob covers them (a probe of `indep-briefs/README.md` gives `project-overlay`). A `sgx1/**` glob would have let the fault come back.
  4. ACT-PATHMAP-NS-1 called the same kind of change "(a) by effect" only because it came before the operator's rule table. Under the table it is (b).
- **risks:**
  - F1 and F2 below.
  - The first store refresh after the commit re-judges every file in the lexical index, because the map is one of its judges. This is a one-time cost.
- **lessons:** an ACT that adds tracked files should run the structural pass on its clone after `apply`. ACT-W2-149-INSTALL-1 rehearsed only the launch script (the package's Q2).
- **proposed_decisions:** none of my own. Q2's template line is the CTO's to adopt, and I agree with it (check 5).
- **unresolved:** none.
- **recommended_next_action:** bring it to the owner for `yes ACT-PATHMAP-NS-2 b1985584`, and put F1's one line in the message so the yes also covers the briefs becoming searchable. The bundle stays as it is, so the hashes hold. Then the owner's operator applies it by hand, as in §5.

## The checks

**1. Exactly one path and its comment, in `project-overlay`: yes.**
- **Hashes:** I recomputed every sha256. `manifest.json` is `b19855849e1e5af58e20dee37145eb14c752b43a12a036d3c88eef1f23678c10`, which agrees with the package, this brief and the owner's line `b1985584`. Each other file equals the manifest's full hash and the package's table: `apply.sh` `0979ddc526fc…`, `list.txt` `984df45a3ecc…`, `path-map.patch` `297aee88ac26…`, `rehearsal.log` `fa0f667547f8…`, `before/` `44f99ea563cb…`, `after/` `7c69c414c0e7…`.
- **`before/` is the live map:** `cmp` exits 0, and the sha256 is `44f99ea563cb59ddd2e0f143e7d7f7c6869c358390fc7b18dbaffc1a4fba7f70`. No commit has touched the map since ACT-SETS-GLOBS-1, and it shows as unmodified in the main tree.
- **`after/` is `before/` plus the patch:**
  - Running `patch -o` onto a copy of `before/` gives a file identical to `after/`.
  - `diff` shows `133a134,135`: the comment line and `- "governance/project/indep-briefs/**"`, inside `project-overlay.paths`, between `indep-walls/**` and `operator/**`.
  - Parsed as YAML, the only difference is that one element.
  - The file mode stays 644.

**2. It fixes the fault and nothing else changes: yes.**
- **Fault fixed, no overlap:** I checked this at today's head in a fresh clone.
  - Before, `gov.check.pathmap` exits 1 with exactly 5 × PATH_NO_NAMESPACE.
  - After, it exits 0. Each brief matches `['project-overlay']` only, and no tracked path matches more than one namespace.
  - Probes: `indep-briefs/sgx2/new.md` gives `project-overlay`, and `indep-briefsX/a.md` gives none.
- **What the namespace grants or refuses:**
  - Nothing at the guard. `pretooluse.py` reads only the map's `sets_root_hidden`, `session_hidden` and `write_refused` blocks, and `role_reads.py` reads only `role_paths`. No code under `.claude/hooks` or `src/gov/guard` reads `namespaces`.
  - Outside the guard, the namespace decides three things:
    - the structural check;
    - the lexical index: `gov.secrets.indexable` refuses a file with no namespace;
    - the vectors: `embedding_policy: embedded`.
- **No widening of reads or writes:**
  - No guard rule names the folder, so every role could already read it.
  - A namespace grants no writes.
  - The briefs' integrity is held elsewhere: a change to them is (O) under the `walled-sessions` row, and `indep_launch.py` launches a brief only against its approved sha256.
  - The one new effect is that the briefs become searchable (F1).
- **Compared with `indep-walls/**`:** it is held the same way (in `project-overlay`, embedded, with no read refusal in the repository).
  - The `indep-walls/**` glob in `sets_root_hidden` is the walls' folder under `~/gov-os-eval`, not this repository folder.
  - The walls are kept from the briefs by two things this ACT does not touch: `tree-exclude.txt` and the walls' limited tools.
  - The `walled-sessions` row's (O) covers changes to the briefs themselves. It is not hit here, because the `path-map` row matches `path-map.yaml` first.

**3. The class and route: right.**
- The change is in none of the `path-map` row's `only_added` lists and touches no ratchet key, so the row's `else: b` applies.
- `act_class.py`, with its installed rule table (identical to the repository's copy, `cmp` 0), gives class b with no hits.
- Rows 76 and 87 keep path-map ACTs out of the agent's queue before 2026-11-11 20:02Z. So the route is the owner's yes, then the operator by hand.

**4. `apply.sh` is safe: yes.**
- **`check`** only hashes and prints.
- **`apply`:**
  - It refuses an unknown map state (exit 3) and a link in the map's place (exit 3).
  - It refuses a frozen copy that does not hash as listed (exit 4), before any backup or write.
  - Running it twice changes nothing.
- **`undo`:**
  - It restores byte for byte: `cmp` 0, mode 644, and `git status` in the clone is empty.
  - It refuses a later change to the map (exit 3).
- **Backup:** it equals `before` and lands under `.gov-runtime/`, which git ignores (`.gitignore:18`).
- **Commit line:** I ran it with a stray staged file elsewhere (`CLAUDE.md`).
  - It committed only the map, with `Role: owner`, and left the stray file staged and uncommitted.
  - `git revert` of that commit restored `44f99ea563cb`.

**5. The package's two questions.**
- **Q1, read refusals for the briefs folder:** agree with (a), none. The briefs hold rules and counts, never cases, labels or seeds, and the walls are already kept from them. A refusal would only block the CTO and leads who launch them.
- **Q2, `gov.check.pathmap` in every ACT's rehearsal:** agree, and for every ACT, not only installs. It takes about a second (the W1-08 path-map file about six) and would have caught this fault.

## Findings

**F1. The package does not say that the namespace also brings the five briefs into the search store.** Scope: in.
- Today, `gov.secrets.indexable` refuses any file with no namespace, so the briefs are in neither the lexical index nor the vectors.
- After the ACT they are governance memory, embedded, with no `lexical_policy`, so both indexes take them.
- The operator's own commit on `w2/integrate` starts that refresh through the main tree's `reference-transaction` hook (`gov rebuild --integration`).
- From then on, `gov retrieve` can return the briefs to every guarded session, the W2-56 tuner included.
- Suggested line for the message: "the five briefs become searchable by every session at the store refresh the commit starts; reads of them were already open."

Ordinary work: yes, because any ordinary search about the experiment can now return the briefs.
Consequence: other, because no refusal is lost. Every role could already read these files. They hold rules and counts, not cases. The walls cannot search memory, and their trees leave out this folder and `.gov-runtime/**`.

**F2. If the hand commit lands while the operator agent is applying another ACT, the freeze refuses it, and §5 does not say what to do then.** Scope: out, because it applies to every hand commit of a control path, not to this revision.
- While `act-in-progress.txt` exists, the `reference-transaction` hook runs `freeze_gate.py`. By its comment (I did not run it), the gate refuses updates that touch the operator's control paths, and the `path-map` row is `control: true`.
- The map would then stay applied but uncommitted.
- One line in §5 would cover it: wait for the agent's ACT to finish, then run the commit line again.

Ordinary work: yes, because it needs only a timing coincidence, no construction.
Consequence: other, because it fails closed. Nothing is lost; re-running the commit line or `apply.sh undo` settles it.

```verdict
{"kpis": [{"kpi": "act-pathmap-ns-2", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
