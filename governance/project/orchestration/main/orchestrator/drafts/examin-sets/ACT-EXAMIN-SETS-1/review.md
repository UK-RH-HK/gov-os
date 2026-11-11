## Round 1

Reviewer: independent-auditor, claude -p session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author. Brief sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a (checked). manifest.json sha256 97d45565ec5c5d03a468ee3a635143f992b6542503ebd816854ea837436dc813 (computed). Every `files` hash matches. The bundle under `acts/` is byte-identical to the copy under `drafts/examin-sets/` (`diff -r`), and the rehearsal ran that copy.

Method: a `--no-hardlinks` clone of `w2/integrate` (b2a33d7b50e4; its map is fb52ab2dc756, the frozen before), with HOME planted under my TMPDIR and dummy files under the planted `gov-os-eval` and in the clone's tree. Nothing live was written. The real sets root and the run folders were never opened.

### The six checks
1. **Touched list and path rule: pass.** In my clone a plain `apply.sh apply` changed only `governance/project/path-map.yaml` (fb52ab2d… → b1ffdb0b…, byte-equal to `after/`, mode kept). Nothing changed in HOME, and apply.sh has no crontab use. The operator's own `live_path_refs` returns None for apply.sh and both checks. apply.sh reaches the bundle through `dirname "${BASH_SOURCE[0]}"`, acts on `$PWD/<path>`, and has no live path and no `cd` to the repository or HOME.
2. **Undo: pass.** In the clone, undo from the applied state gave the before bytes (cmp equal, `git diff` clean, mode 640 kept), and a second undo said "nothing to undo". The rehearsal log shows G3/G4 (undo from the applied state, original byte for byte).
3. **Rehearsal: pass.** The log is a run of this apply.sh (tools/rehearse.sh, `ACT=$D/ACT-EXAMIN-SETS-1`) in a clone of w2/integrate at 625aa084fa02, and it ends `failures: 0`. See F2.
4. **Checks: pass.** From the applied clone: `PYTHONPATH=src python3 -m gov.check.pathmap` exit 0 (also 0 on the pinned interpreter). Check 2 (the YAML probe) exit 0, and exit 1 on the before map, so it tells the two apart. Both have count null, as the manifest states. See F1.
5. **Class: (a).** Row `path-map` of class-rules.yaml. `act_class.py` on the bundle votes `a` ("only the additions the row allows"), with no script hits. The YAML differs only by two new `evaluation_sets` entries, each with a non-empty `hidden` (`new_entries`/`new_entry_needs` hold), and no ratchet key changes. The row does not check a new entry's `visible` or `measures` keys, but in the code neither grants anything: `visible` is read only by `set_fault` (shape) and by `measure`'s quoting refusal part, and `measures.roles` only adds hidden globs to the roles it names (`reads._hidden`).
6. **Guard replay: pass, replay_refused [].** On the live map's base, the 161 cases I ran give the same answers before and after: Read, Write, Grep and Bash on each hidden half under the planted sets root and in the tree; the visible folders; W2-81's questions; `src/`; the `--sets-root <root>` line; seven sessions (five measured roles, the CTO, a lead). All 91 hidden-half cases are refused before and after. The wildcard `fixtures/evaluation/*/hidden/**` in `sets_root_hidden` (ACT-SETS-GLOBS-1) already refuses them. So no call turns from allowed to refused.

### The four questions
- **(1) Widening: none.** No role gains a read or write. In addition to the identical 161 answers, I removed the wildcard from both maps to isolate the entries. The entries then turn 58 calls from allowed to refused: Read, Write and Grep under the sets root, and Read, Bash and Write in the tree, for engineer, research, product-spec, test designer and auditor. They turn none from refused to allowed. The orchestrator's answers do not move (it is not in `measures`).
- **(2) Class (a): right**, by the path-map row and by the operator's code vote (above).
- **(3) Decided by sha256: yes.** before = list.txt's before hash, applied = its after hash, anything else is "other" and refused with exit 3, touching nothing. Tested in the clone: a changed map (apply, undo, check and verify all refuse, file untouched), a missing map (apply and undo refuse, nothing created), a link (apply, check and undo refuse, the link target untouched). Two more refusals are on top of the hash and only add refusals: a link is refused before hashing, and a frozen copy that does not hash as listed exits 4 (tested on a tampered copy of the bundle under my TMPDIR, map untouched, no `.act-tmp` left).
- **(4) Store kept_out: yes.** `gov.retrieval.lexical.kept_out` on the clone, before and after alike, names as `evaluation-fixtures` (not indexed) each of `fixtures/evaluation/examin/{hidden,visible,hidden/visible}/q01.yaml`, `examin/XCHECK-r1.md`, `examin/DRAW.txt` and `adoption-proving-ground/{hidden,visible}/q01.yaml`. `tests/acceptance/W2-81/questions/**` stays indexed, as the package intends ("as today"). The ACT leaves `namespaces` alone.

### Findings
- **F1. KPI 4. Scope in. ordinary_work yes. Consequence: other.** The rehearsal does not run the manifest's checks as written. D1 runs `gov.check.pathmap` on the pinned interpreter, not `python3`. Manifest check 2 is never run: D2 is a different command (a before/after comparison). So the log shows no exit for check 2 as written. *Evidence:* rehearse.sh's D1 and D2 lines against `manifest.json` `checks[]`. I reproduced both checks as written in the clone (exit 0, count null; check 2 exits 1 on the before map), and the operator's G8 reruns each check (`operator_run.py`, the `check_ok` loop in the dry run). So nothing is wrong today. *Fix:* the next bundle's rehearsal runs each `checks[].cmd` exactly as written with `bash -c` from the clone and prints its exit and count.
- **F2. KPI 1/3. Scope in. ordinary_work yes. Consequence: other.** The rehearsal's only real apply (C1) ran with `ACT_BACKUP_BESIDE=1`, which also writes `path-map.yaml.bak-<stamp>-ACT-EXAMIN-SETS-1` beside the map. That file is not in `touched`, and `undo` does not remove it. The plain apply the operator runs was rehearsed only as a no-op (C6). *Evidence:* rehearse.sh lines C1 to C3. My plain apply in the clone changed only the listed file. *Fix:* rehearse the plain apply. Say in FOR-THE-OWNER.md that a hand run with the backup leaves an untracked file that undo keeps.
- **F3. KPI 1. Scope out. ordinary_work yes. Consequence: other.** apply.sh's header says to rebuild with "tools/insert_entries.py (beside this bundle)". Beside the copy under `acts/` there is no `tools/`; the tool is in `drafts/examin-sets/tools/`. Text only, no effect on the run. *Fix:* name the drafts path in the next bundle.
- **F4. KPI 1. Scope out. ordinary_work yes. Consequence: other.** apply and undo write `cat "$src" > "$f.act-tmp"` then `chmod` and `mv`. A link planted beforehand at `<map>.act-tmp` would be followed, writing the frozen copy into its target. That needs a planted link beside a tracked file; nothing in this ACT creates one. *Fix (later bundles):* `rm -f "$f.act-tmp"` first, or create the temp file with `mktemp` in the same folder.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "4", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "5", "verdict": "pass", "findings": []},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "97d45565ec5c5d03a468ee3a635143f992b6542503ebd816854ea837436dc813",
 "class": "a",
 "reviewer": "independent-auditor, claude -p session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-11T15:49:25+00:00",
 "replay_refused": []}
```

## Round 2

Reviewer: independent-auditor, claude -p session (round 2) started by the CTO (launch_worker.sh, DAEO-r30l); not the author (the author is the CTO's helper a1bb02d66a5427dd2). I checked the brief's sha256: e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a. I computed manifest.json's sha256: e80202922e72b3e55767efceef315b8ead863de443fb4036aab24cb6f9e8674f. Every hash in `files` matches the bundle's bytes.

Method: I made a `--no-hardlinks` clone of `w2/integrate` (08f51ea8c68f), whose map is f4029cfb4942, the frozen before. HOME was planted under my TMPDIR, with dummy set files under the planted `gov-os-eval` and in the clone's tree. Nothing live was written; the live map is still f4029cfb4942 after the review. The real sets root and the run folders were never opened. This round judges the rebuild only.

### The round 2 points
- **(i) The entries are byte-identical to round 1's: yes.** The `>` lines of `diff before after` are 19 lines, with the same sha256 in both bundles (37e2465d…, `cmp` equal). Round 1's before and round 2's before differ only by ACT-W1-01-EXEMPT-3's two `acceptance_exemptions` lines (commit 7b5c3cb94, whose map hashes as f4029cfb…). Round 1's after and round 2's after differ by the same two lines and nothing else.
- **(ii) The chain is the new one: yes.** list.txt and the manifest give f4029cfb4942… → 0ec1d20da86a…. ACT-ACCEPTED-REDS-1's round 2 list.txt gives 0ec1d20da86a… → 5654eca4c139…. The live map and w2/integrate's map are both f4029cfb4942….
- **(iii) Round 1's findings: all fixed.**
  - F1 (fixed): the rehearsal runs each `checks[].cmd` as written with `bash -c` (D1, D2, with Dx on the before map).
  - F2 (fixed): the plain apply is rehearsed (C5), and apply.sh no longer has a backup option (no `ACT_BACKUP`/`.bak` in the script).
  - F3 (fixed): the rebuild hint names `.gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/insert_entries.py`, which exists, as does `build_r2.py`.
  - F4 (fixed): the temp file is made by `mktemp "$f.act-tmp.XXXXXX"`; the rehearsal's J7/J8 show a link at the old fixed name is not followed.
- **(iv) Decided by sha256, refused on the old map: yes.** On the old map fb52ab2dc756, `check`, `apply`, `undo` and `verify` each exit 3, and the file is untouched. The same holds for round 1's after (b1ffdb0b7b3e), a changed map, and a missing map (nothing is created).

### The six checks
1. **Touched list and path rule: pass.** In my clone a plain `apply.sh apply` changed only `governance/project/path-map.yaml` (f4029cfb… → 0ec1d20d…, byte-equal to `after/`, mode 644 kept). `git status` lists only the map, and no `.act-tmp` file is left. The planted HOME's file listing is unchanged, and apply.sh has no crontab use. The operator's `live_path_refs` returns None for apply.sh and for both checks, and `path_rule` does not refuse. apply.sh reaches the bundle through `dirname "${BASH_SOURCE[0]}"`, acts on `$PWD/<path>`, names no live path, and has no `cd` to the repository or HOME.
2. **Undo: pass.** In the clone, undo from the applied state gives f4029cfb… byte for byte (mode kept, `git status` clean). A second undo says "nothing to undo". The rehearsal shows I6/I7 (undo from the committed state, the live map byte for byte) and I9 (undo is refused while REDS is on top).
3. **Rehearsal: pass.** The log is the run of this apply.sh: tools/rehearse_r2.sh sets `EX=$D/acts-r2/ACT-EXAMIN-SETS-1`, in a fresh clone of the main tree's w2/integrate. Its bytes equal `drafts/examin-sets/rehearsal.r2.log`, and it ends `failures: 0` (124 checks).
4. **Checks: pass.** From the applied clone, each check as written with `bash -c`: check 1 exits 0 (it is also 0 on the pinned interpreter), and check 2 exits 0. Both have count null, as the manifest states. On the before map check 2 exits 1, so it tells before from after. Check 1 is a validity check and is 0 on both maps.
5. **Class: (a).** By row `path-map` of class-rules.yaml, the YAML differs only by two new `evaluation_sets` entries. Each entry has a non-empty `hidden`, so `new_entries` and `new_entry_needs` hold, and no ratchet key changes. The operator's `act_class.py` on the bundle votes `a` ("only the additions the row allows") with no script hits, and `commands` is empty. The claim, the code and this review agree.
6. **Guard replay: pass, replay_refused [].** I ran the clone's PreToolUse hook (pinned interpreter, planted HOME) on 343 cases with the before and after maps. The cases cover Read, Write, Grep, Glob, Bash cat and Bash write on both sets' `hidden/`, `hidden/visible/`, `visible/`, `XCHECK-r1.md` and `DRAW.txt`, under the planted sets root and in the tree; W2-81's questions; `src/`; a write to the map; and the `--sets-root <root>` line. Each case ran for seven sessions: the five measured roles, the CTO and a lead. The answers are identical (227 deny, 116 allow on both maps), and every hidden-half case is refused before and after. So no call turns from allowed to refused.

### The four questions
- **(1) Do the entries widen anything? No.** No role gains a read or a write. Beyond the 343 identical answers, I removed `fixtures/evaluation/*/hidden/**` from `sets_root_hidden` in both maps to see the entries alone. The entries then turn 136 calls from allowed to refused, all on the hidden halves, under the sets root and in the tree. They are spread over engineer (28), research (28), product-spec (28), test designer (28) and auditor (24; its tree writes were already refused). They turn none from refused to allowed. The CTO's and the lead's answers do not move.
- **(2) Class (a): right**, by the path-map row and by the operator's code vote.
- **(3) Decided by sha256 alone: yes.** "before" means list.txt's before hash, "applied" means its after hash, and anything else is "other", refused with exit 3, touching nothing. I tested an old map, round 1's after, a changed map and a missing map. Two refusals sit on top of the hash and only add refusals: a link is refused before hashing (I tested a link to the before bytes: all four steps exit 3, target untouched), and a frozen copy that does not hash as listed exits 4 (rehearsal J12).
- **(4) Does kept_out name the new folders? Yes.** `gov.retrieval.lexical.kept_out` on the clone gives the same result on the before and after maps. It names each of `fixtures/evaluation/{examin,adoption-proving-ground}/{hidden/q01.yaml, hidden/visible/q01.yaml, visible/q01.yaml, XCHECK-r1.md, DRAW.txt}` as `evaluation-fixtures` (not indexed). `tests/acceptance/W2-81/questions/**` stays indexed, as the package intends. The ACT leaves `namespaces` alone.

### Findings
- **F1. KPI 1. Scope out. ordinary_work yes. Consequence: other.** The handoff to the operator.
  - *What:* the operator's G1 reads `<scratch>/acts/ACT-EXAMIN-SETS-1/`. That folder still holds the round 1 bundle (manifest 97d45565…, with round 1's review.md). A third copy of round 1 also sits at `drafts/examin-sets/ACT-EXAMIN-SETS-1/` beside `.r1/`. Until the round 2 bundle is put there, a run under `yes ACT-EXAMIN-SETS-1 e8020292` is refused: G5 sees another manifest sha, and apply.sh would report state other. It fails closed, and nothing is touched.
  - *Round count:* `act_rounds` (DEC-1131 (3)) counts verdict blocks across every frozen copy of this ACT id, comparing them by text. A round 1 block carried into this review.md with any change would count as a separate round, which makes three rounds and sends the ACT to the owner.
  - *Evidence:* operator_run.py `g1` (`os.path.join(s["scratch"], "acts", self.act)`), `act_rounds` and `g4`; the `acts/ACT-EXAMIN-SETS-1/` listing.
  - *Fix:* copy `acts-r2/ACT-EXAMIN-SETS-1/` over `acts/ACT-EXAMIN-SETS-1/` as a whole, with this review.md. Round 1's block is either left out or carried byte for byte, never retyped.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": []},
          {"kpi": "4", "verdict": "pass", "findings": []},
          {"kpi": "5", "verdict": "pass", "findings": []},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "e80202922e72b3e55767efceef315b8ead863de443fb4036aab24cb6f9e8674f",
 "class": "a",
 "reviewer": "independent-auditor, claude -p session (round 2) started by the CTO (launch_worker.sh, DAEO-r30l); not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-11T19:40:27+00:00",
 "replay_refused": []}
```
