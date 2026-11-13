# ACT-CLAUDE-COPIES-7: the ACT review (OPERATOR-AGENT-1 §3, G4)

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session, not the ACT's author. Worked under the operator's fixed reviewer brief (`~/gov-os-operator/install/reviewer-brief.md`, sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`, the hash in the install's `APPROVED`) and `governance/project/briefs/JUDGEMENT.md`.
- Manifest sha256: `78de1c5fe9198ea3a3982e7d8557397b5b5ddce8682e2f85b9b6cfc5c4f1fb02` (re-hashed).
- Reviewed on integrate `02873772c` (it moved from `c0918f144` during the review by one `.tickets/` commit, which touches no bundle path), with `w2/W2-98` at `3a86f11c3981`, the approved commit.
- All runs in fresh `--no-hardlinks` clones under `/tmp/claude-1000/rev-copies78-430190/`, HOME planted at an empty folder, every pytest through `heavy_slot.sh` with `-p no:cacheprovider` and TMPDIR outside the repository. Refused reads: 0.

task: ACT-CLAUDE-COPIES-7 (W2-98, DAEO-wi46)
decisions: DEC-1163 (8), DEC-315, DEC-1112 (3), DEC-1156 (3), DEC-1057, DEC-1104, DEC-801, DEC-808, DEC-1010, DEC-1014, CAP-33

Classification: 0 blocking; F1 to F4 are rows (consequence other, or not reachable in ordinary work).

## Per check
1. **Touched list, generation and path rule: PASS.**
   - The bundle's file hashes equal the manifest's; `list.txt` equals `touched`; no unnamed file in the bundle.
   - Integrate with W2-98 merged (clean merge): the twelve sources (kernel, root `.rulesync`, `template/.rulesync`) are at CIT-P §3's hashes (`34500d5e`, `b18ebd98`, `3ddd0e1a`, `9174042b` each). W2-98's commit after the CIT-P's recorded head (`f0259229e2b5` to `3a86f11c3981`) touches only the CIT-P and the probe record.
   - The reviewer's own generation on that tree (integrate's `compose()` for each root source, rulesync 24.0.0 with portability's GENERATE arguments into a fresh folder, `--write-templates`) gives the four `.claude/skills/spec-writing/` files byte-equal to `after/`. The only other files it changes are COPIES-8's four copies (disjoint paths), and rulesync's only other differing output is `.claude/settings.json`, not written, as in COPIES-5 and -6.
   - `apply.sh` reaches its bundle through its own folder and writes under `$PWD`; neither it nor either check names a live repository or HOME path or `cd`s to one.
2. **Undo: PASS.** In the clone, `apply` creates exactly the four files; `undo` removes them and the tree is clean (F1: an empty folder stays). The rehearsal log shows the undo, the re-apply, and the commit, undo, commit sequence ending in an empty diff.
3. **Rehearsal: PASS.** A real run of this `apply.sh` in clones with a planted HOME, ending `failures: 0`; its build base `df9d442e8f82` and its re-check on `2bf4430f41d4` differ from today's head only in paths the ACT does not read.
4. **Checks: PASS.**
   - Check 1 (4 files): red before the apply, exit 0 after (4 OK lines).
   - Check 2 (the 12 sources): exit 0 before and after on the merged tree; **exit 1 on integrate without W2-98** (measured), so a run before the hand merge's merge commit is refused at G8. That is the order the package asks for: the merge commit, then this ACT, then the checks.
   - `apply.sh check` refuses a stray file at a target (exit 3) and a second apply (exit 3); an unknown step exits 2.
   - On the fully landed tree (integrate, W2-98 merged, this ACT, then COPIES-8) both checks of both ACTs are green and portability exits 0 with no findings.
5. **Class: (b).** The operator's `act_class` (run read-only on the bundle) gives class `b`, row `agents-skills-kernel` for all four files, no script hits; this matches the claim and COPIES-1 to -6.
6. **Guard replay: not applicable.** No path-map or deny entry is added; `replay_refused` is empty.

**The suites (reviewer's runs):**
- Integrate, W2-98 merged, this ACT, without COPIES-8: W2-98 502 passed; W2-11 199 passed, 1 skipped; W1-33 112 passed; W1-38 42 passed (159 deselected by the conftest); **adapters 2 failed** (`test_w2_153_compose.py::test_the_twelve_sources_are_the_composition[]`, `test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition`); **W2-153 2 failed** (`test_s3_each_role_source_is..._body[orchestrator-.rulesync]`, `test_s3_guard_the_check_finds_no_role_source_drift_in_this_repository`). These four are COPIES-8's pending orchestrator source, not this ACT's.
- The same tree with COPIES-8 applied too: adapters 102 passed, W2-153 66 passed, W2-98 502 passed, W2-11 199 passed and 1 skipped. No red remains, and the ACT brings none.

**Sound:** the bytes, the order through check 2, the independence from COPIES-6 and -8 (disjoint paths, both orders give the same bytes), and the class.

## Findings (none blocks)
- **F1** (check 2, scope in): after `apply.sh undo`, the empty folder `.claude/skills/spec-writing/` is left behind. Git does not see it and portability reads the window's own four `GENERATED_DIFFERS`, nothing more (measured), so nothing is lost or opened.
  - Ordinary work: yes, because any undo of this ACT leaves it.
  - Consequence: other.
  - What would reverse it: a skill loader or check that treats an empty skill folder as a broken skill.
- **F2** (check 4, scope in): every before-hash is "absent", so `apply.sh check` passes in any folder, including one that is not the repository; only check 2 (G8, after the apply) notices a wrong folder, after four files were written into it.
  - Ordinary work: no, because the operator runs the bundle in its clone and the repository by construction, and the by-hand route starts with a `cd` to the repository.
  - Consequence: other.
  - What would reverse it: an operator run whose cwd is not the repository.
- **F3** (outside the bundle, scope out): the CIT-P at `3a86f11c3981` still reads `status: PROPOSED` and `owner_approval: none yet`, while the register records the owner's approval at that commit (DEC-1163 (8)). The package's step 1 says the line is written before the merge. If the merge goes in without it, the merged record contradicts the register.
  - Ordinary work: yes, because it is one hand step in the merge sitting.
  - Consequence: other.
  - What would reverse it: the `owner_approval:` line written on W2-98 before the merge commit (a `docs/` edit that leaves check 2 green).
- **F4** (check 3, scope in): the rehearsal and the package measured integrate `df9d442e8f82` and `2bf4430f41d4`; integrate is now `02873772c`. The difference touches no bundle path and no source, and the reviewer's runs on today's head agree with the package's figures.
  - Ordinary work: yes, because integrate moves after a bundle is built.
  - Consequence: other.
  - What would reverse it: any of the twelve sources or the four targets differing at apply time.

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "pass", "findings": []}, {"kpi": "check 2", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 3", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 4", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 5", "verdict": "pass", "findings": []}, {"kpi": "check 6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "78de1c5fe9198ea3a3982e7d8557397b5b5ddce8682e2f85b9b6cfc5c4f1fb02",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T12:16:00+00:00",
 "replay_refused": []}
```
