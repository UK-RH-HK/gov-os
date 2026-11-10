# ACT-PATHMAP-NS-2: the fixed briefs' folder placed in a path-map namespace (DEC-1101, DEC-1113)

## 0. What the owner says
Class **(b)**: the owner's yes, then the owner's operator **by hand** (the operator agent takes no path-map ACT before
2026-11-11 20:02Z: DECIDED-NOT-DONE rows 76 and 87). The line, on its own line:

yes ACT-PATHMAP-NS-2 b1985584

- **By:** a helper of the CTO (orchestrator `DAEO-sdxk`), 2026-11-10. Built and rehearsed in a fresh clone at `baac0b2c2f61`.
  **Nothing live changes until it runs.** The live map was only read.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-PATHMAP-NS-2/`. **Manifest sha256
  `b19855849e1e5af58e20dee37145eb14c752b43a12a036d3c88eef1f23678c10`.**

## 1. The fault
ACT-W2-149-INSTALL-1 (`baac0b2c2f61`) put five tracked files under `governance/project/indep-briefs/sgx1/`. Its package said
the path map was untouched, and no namespace matches `governance/project/indep-briefs/**`. So `python3 -m gov.check.pathmap`
reports 5 x `PATH_NO_NAMESPACE` (and nothing else), and `tests/acceptance/W1-08/test_w1_08_path_map.py::
test_every_tracked_path_matches_exactly_one_namespace` is red. That turns `gov check` red, which refuses every close and
the re-pin. What the install's review missed: its rehearsal ran the launch script, not the structural pass over the new
tracked paths. (ACT-PATHMAP-NS-1 placed `indep-walls/**` for the same reason, one folder earlier.)

## 2. The class and the route
**(b).** `governance/project/operator/class-rules.yaml` (identical to `~/gov-os-operator/install/class-rules.yaml`: `diff`
is empty), the `path-map` row, its rule line: `why: "path map: items only added to refusal lists (sets_root_hidden,
role_paths denies, a new evaluation_sets entry with its hidden globs) tighten (a) (SANDBOX-SEAL-1); any other change
alters a control (b) (GUARD-SETS-1); a ratchet list ... (O) ..."`, with `else: b`. A namespace path in
`project-overlay.paths` is in none of the row's `only_added` lists, so it is "any other change". The operator's own
`act_class.py` on the bundle (read-only) gives `{"class": "b", ... "row": "path-map", "hits": []}`.

Route: the owner's yes, then the owner's operator by hand (the steps in §5). The agent's queue stays closed to a path-map
ACT until 2026-11-11 20:02Z (rows 76 and 87).

## 3. The change (one comment line and one path)
In `governance/project/path-map.yaml`, `project-overlay.paths`, after `governance/project/indep-walls/**` (line 133):
```
+      # ACT-PATHMAP-NS-2 (DEC-1101, DEC-1113): the walled sessions' fixed briefs (ACT-W2-149-INSTALL-1)
+      - "governance/project/indep-briefs/**"
```
Embedded, restricted, every role may read, as the namespace's other overlay folders. No hidden glob, role denial or
sets-root entry changes. Map sha256 before `44f99ea563cb59ddd2e0f143e7d7f7c6869c358390fc7b18dbaffc1a4fba7f70` (verified
the live map at the time of writing; `apply.sh check` is the guard if it moves), after
`7c69c414c0e747cbf40b84db5079893f8dd611edfdcef3ad09abc121f4d6eb7e`; mode 644 kept.

| File | sha256 (12) | What |
|---|---|---|
| `manifest.json` | `b19855849e1e` | touched, files, one check, rehearsal |
| `apply.sh` | `0979ddc526fc` | `check`, `apply`, `undo`, `verify`; from the repository root |
| `list.txt` | `984df45a3ecc` | the one file, before and after sha256 |
| `path-map.patch` | `297aee88ac26` | the two added lines |
| `before/`, `after/` | `44f99ea563cb`, `7c69c414c0e7` | the frozen map and its result |
| `rehearsal.log` | `fa0f667547f8` | the rehearsal (below) |

`check` is read-only and prints `state before|applied|other (sha256 ...)` (exit 0, 0, 3). `apply` runs only from `before`,
copies the live map first to `<bundle>/backup/path-map.yaml.<UTC stamp>` (`ACT_NO_BACKUP=1` skips it; the folder is under
`.gov-runtime/`, so the repository gets no stray file), then moves the frozen result in, mode kept. `undo` puts the frozen
original back byte for byte, only when the map is the ACT's own result.

## 4. The three checks, and the rehearsal (DEC-1057; `rehearsal.log`)
1. **Exactly one namespace.** After the change each of the five files matches `['project-overlay']` and nothing else, and
   all 3879 tracked paths match exactly one namespace (0 with none, 0 with several; `PATH_MULTIPLE_NAMESPACES` absent). No
   other glob overlaps: `governance/project/*` is one folder deep, `governance/project/operator/**` and
   `.../orchestration/**` are other folders.
2. **Role read refusals: none exist for `indep-walls/**` in the repository, so none are missing.** See question 1.
3. **Other tracked paths without a namespace: none.** Before the change: 5 x `PATH_NO_NAMESPACE`, exactly the five files,
   no other code, no other path (3879 tracked, 5 with none).

Rehearsal in a fresh clone at `baac0b2c2f61` (HOME `/home/usain`): before, `gov.check.pathmap` exit 1 (5 findings) -> `check`
`state before` -> `apply` -> `verify` -> `check` `state applied (sha256 7c69c414c0e7)`; `diff` against the frozen before is
exactly the two lines -> `gov.check.pathmap` **exit 0, no findings** -> `test_w1_08_path_map.py`: **28 passed, 6
deselected** -> `guard4_check.py --settings <clone>` (the clone's hook, settings line and applied map): **453 run, 0
failed, PASS** -> a second `apply` changes nothing; a later change to the map makes `check` exit 3, `undo` and `apply`
refuse and leave it; a tampered frozen copy makes `apply` exit 4 -> `undo` **byte for byte** (`cmp` exit 0, clone `git
status` empty; `gov.check.pathmap` red again, as before). The rehearsal ran on a copy of the bundle so the live bundle has
no backup folder; the copy's `apply.sh`, `list.txt`, `before/` and `after/` equal the live bundle's (`diff` empty).

## 5. The message for the owner's operator (by hand; about two minutes)
yes ACT-PATHMAP-NS-2 b1985584

> **ACT-PATHMAP-NS-2 (DEC-1101, DEC-1113): the path map places `governance/project/indep-briefs/**` in `project-overlay`; one comment line and one path.** Class (b), by hand.
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/acts/ACT-PATHMAP-NS-2
> sha256sum $G/manifest.json      # expect b19855849e1e5af58e20dee37145eb14c752b43a12a036d3c88eef1f23678c10
> git status --short              # the map must not be listed (other lines are the CTO's and stay uncommitted)
> bash $G/apply.sh check          # expect: state before (sha256 44f99ea563cb)  (anything else: stop, tell the CTO)
> bash $G/apply.sh apply          # expect: backup ...path-map.yaml.<stamp> (sha256 44f99ea563cb), then state applied (sha256 7c69c414c0e7)
> bash $G/apply.sh verify         # silent, exit 0
> PYTHONPATH=src python3 -m gov.check.pathmap; echo $?   # expect: 0, no output before it
> git commit -m "ACT-PATHMAP-NS-2: governance/project/indep-briefs/** placed in project-overlay (the five fixed briefs had no namespace)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1113" --trailer "Role: owner" -- governance/project/path-map.yaml
> ```
> The commit names its one path, so a staged file elsewhere in the index (the CTO's) is not swept in.
> **Undo:** `git revert <the commit>`, or before the commit `bash $G/apply.sh undo` (expect `state before (sha256 44f99ea563cb)`;
> rehearsed byte for byte). If the map has changed since, `undo` refuses and says so; the backup under `$G/backup/` is the hand copy.

## 6. Questions for the CTO
1. **Should `indep-briefs/**` carry role read refusals the way the walls' folders do?** Found: the repository's
   `governance/project/indep-walls/**` has none either. The `indep-walls/**` entry in `sets_root_hidden` is the folder
   under the sets root (`~/gov-os-eval/indep-walls/`), outside the repository; `role_paths` names only the engineer and the
   test designer; `held-out.yaml` has no `indep` entry; the guard's hook names neither folder. The walls' blindness comes
   from the wall hook and from `tree-exclude.txt` (which leaves the briefs folder out of every wall), and the class row
   `walled-sessions` makes both folders (O) to change. The briefs are approved text every role reads. **Options:** (a) none,
   as for `indep-walls/` (cost: nothing; this ACT stays one line); (b) a `role_paths` or `sets_root_hidden` addition for the
   six roles (cost: tightening only, class (a) by the `path-map` row, but it needs its own rehearsal and the CTO and leads could
   no longer read the briefs they launch). **Recommendation: (a). Confidence: medium-high.** It blocks nothing here.
2. **Process:** an install package that adds tracked files under a new folder should rehearse `gov.check.pathmap` and the W1-08
   path-map test file. Recommendation: add it to the ACT template's rehearsal list. Confidence: high. Blocks nothing.

## Review: pending

[DEC-1101, DEC-1113, DEC-1057, DEC-1104 (2), OPERATOR-AGENT-1 §2]
