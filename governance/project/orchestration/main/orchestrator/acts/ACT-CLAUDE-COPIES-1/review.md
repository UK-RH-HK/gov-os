# ACT-CLAUDE-COPIES-1 — the ACT review (OPERATOR-AGENT-1 §3, G4)

Transcribed by the CTO's helper session from the reviewer's return, word for word in substance (2026-11-09 23:18 UTC).
Reviewer: an independent-auditor in-session subagent (agent `a7f7bacf0bdf6b7e5`), fresh, read-only on the live tree
and the bundle, not the ACT's author, under the operator's fixed reviewer brief (`reviewer-brief.md`, sha256
`e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`).

## Summary
All six checks pass; the class is (b); three findings, none blocking. Manifest sha256
`5d3a18832b9b78e1e5a057cba470a9613da0e83447f0edf0fac2cbb6c24891fc`, unchanged at the end. Live HEAD moved during the
review (`336828354` → `f8b242dc9`); none of the new commits touches the 19 paths, `template/governance/kernel/` or
`src/gov/adapters/`.

## Check 1 — the touched list is complete and exact, and the script is relative: PASS
- **Before hashes.** The 19 before hashes equal the live files, at the start and at the end. The eight
  `.claude/templates/*` files, and the folder itself, are absent live.
- **Byte copies.** The four `.rulesync/skills` after-copies equal the kernel skills. The eight template copies equal
  the kernel templates, and the eight names are W2-153 S4's list.
- **The orchestrator source.** It keeps the live front matter, with the kernel role's body; the only change is the
  retired-briefs line.
- **The generated files.** The reviewer ran rulesync 24.0.0 itself on a copy of `.rulesync` with the five
  after-sources: 44 files written. The six touched generated files are byte-equal to the after-copies. The only other
  file differing from live is `.claude/settings.json`, which portability compares only after its held-out step
  (DEC-635). In the clone, portability gives the same 6 findings as `rehearsal.log` at HEAD, and `[]` after the apply.
- **The changed set.** After the apply, exactly the 19 paths change (11 modified, 8 new) and no file mode changes.
  The planted HOME stays empty and `commands` is `[]`.
- **The path rule.** `apply.sh` reaches the repository only as `$PWD/<path>` and the bundle through its own folder.
  It names no absolute, `~` or `$HOME` path and never `cd`s to either. The check is relative. `validate_manifest` and
  `path_rule` pass.

## Check 2 — the undo is tested: PASS
- `apply.sh undo` restores all 19 files byte for byte, removes `.claude/templates`, and leaves the trees clean.
- After a committed apply, the undo plus its commit leaves the tree equal to the start commit.
- `rehearsal.log` lines 11 and 12 show the same.

## Check 3 — the rehearsal is real: PASS
- The builder runs the hashed `apply.sh` in a fresh `--no-hardlinks` clone at the live HEAD with a planted HOME,
  then writes the log and hashes it into the manifest.
- Both logs end with `failures: 0`.
- The reviewer's own re-run in its clone, from a frozen copy of the bundle, reproduced every step. §5 with its
  commits gave the same diffstat: 19 files, 320 insertions, 23 deletions.

## Check 4 — the checks are right: PASS
- The one check exits 0 after the apply, as stated (count null).
- It catches bad states: exit 2 before the apply, exit 1 on a changed copy.
- `apply.sh check` refuses a moved file: `moved: <path>`, exit 3.

## Check 5 — the class: PASS, (b)
- By §2's table: `.claude/agents|skills/**` are generated role files and skills, (b); `.rulesync/**` changes other
  than deny additions are (b).
- `act_class.classify` gives `b` with no hits: six files `agents-skills-kernel`, eight `claude-rest`, five
  `rulesync-other`.
- Nothing raises it to (O). §5's `Role: owner` trailer is how a (b) change is committed by hand. It is not a
  `Role: owner` record in §2's sense.

## Check 6 — the guard replay: PASS (not applicable)
No path-map or deny-list entry is added, so `replay_refused` is `[]`.

## Findings (none blocks)
- **F1** (check 4, scope in): the manifest's check covers only the 12 byte copies, not the six generated files or the
  composed orchestrator source.
  - Ordinary work: yes. The operator's touched-file hashes and G8's changed-set check pin all 19 files, and the
    CTO's post-apply portability covers the generated ones.
  - Consequence: other.
  - Reversed by: an apply path that commits without the touched-hash comparison (§5 by hand runs only `wc -l`).
- **F2** (check 5, scope out): §2's prose table names no `.claude/templates/**` row; the installed
  `class-rules.yaml`'s `claude-rest` row covers it as (b).
  - Ordinary work: yes. The ACT is (b) on its agents and skills either way.
  - Consequence: other.
  - Reversed by: an owner ruling that only the prose table counts, which would make the templates (O).
- **F3** (checks 1 and 2, scope out): `apply.sh` has `set -u` but not `-e`, so a failed write still exits 0.
  - Ordinary work: no. A failed write of 19 small files on a local disk is not ordinary, and the touched-hash check
    and G8's undo would catch it.
  - Consequence: other.
  - Reversed by: §5 run by hand on a full or read-only disk.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F3", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": []},
          {"kpi": "4", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "5", "verdict": "pass", "findings": [{"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "5d3a18832b9b78e1e5a057cba470a9613da0e83447f0edf0fac2cbb6c24891fc",
 "class": "b",
 "reviewer": "independent-auditor, in-session subagent of the CTO's helper session ad44f5fe; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-09T23:17:48+00:00",
 "replay_refused": []}
```
