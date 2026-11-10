# ACT-CLAUDE-COPIES-2 — the ACT review (OPERATOR-AGENT-1 §3, G4)

Transcribed by the CTO's helper session from the reviewer's return (independent-auditor in-session subagent, agent
`abc872ed646039e63`; fresh, read-only, not the ACT's author), under the operator's fixed reviewer brief (sha256
`e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`).

## Summary
- All six checks pass; class (b); four findings, none blocking.
- Manifest sha256 `36ab6b62950f3e26f97779d68a299e4c66b1c421438a572477a4606ec75c3fed`; all 23 listed files hash as
  stated.

## Check 1 — the touched list is complete and exact, and the script is relative: PASS
- **Before hashes:** all 10 equal the live tree's at `1bf23a0b3e77`.
- **The two skill sources:** byte-equal to the kernel skills.
- **The generation:** rulesync 24.0.0, run by the reviewer on the live `.rulesync/` with the two after-sources
  overlaid, gives the six agents and two skills byte-equal to the after-copies. Every other output equals the live
  tree, except `.claude/settings.json` (F4).
- **The agents:** each one's only front-matter change is an added `skills:` entry, and each body equals its role
  template's body, per `ROLE_TEMPLATES`:
  - engineer → test-driven-development;
  - independent-auditor → audit;
  - independent-test-designer → test-design;
  - orchestrator → orchestration;
  - product-spec → change;
  - research → discovery.
  `tools` is unchanged in all six.
- **The changed set:** after the apply, exactly the 10 files change; the planted HOME stays empty; crontab is
  untouched.
- **The path rule:** `validate_manifest` and `path_rule` pass.

## Check 2 — the undo is tested: PASS
- `apply.sh undo` restores all 10 files byte for byte.
- §5 run literally with both commits leaves an empty diff against `1bf23a0b3`.

## Check 3 — the rehearsal is real: PASS
- `rehearsal.log` is the builder's run of this `apply.sh` in a fresh clone with a planted HOME, and ends
  `failures: 0`.
- The reviewer's own run reproduced every step: portability after the apply exits 0 with `[]`, and the live tree is
  unchanged.
- The §5 log (sha `3bc785c1…`) ends `failures: 0`.

## Check 4 — the checks are right: PASS
- The check exits 0 after the apply and 1 before.
- It covers only the copies (F1).

## Check 5 — the class: PASS, (b)
- `act_class.py`: (b), no hits; 8 files `agents-skills-kernel`, 2 `rulesync-other`.
- No (O) trigger applies.
- The claimed class, the code's and the reviewer's agree.

## Check 6 — the guard replay: PASS (not applicable)
No path-map or deny entry is added; `replay_refused` is `[]`.

## Findings (none blocks)
- **F1** (check 4, scope in): the manifest's check covers the template copies and the two skill sources, not the
  eight generated files.
  - Ordinary work: yes. G7 and G8 pin all 10 files by hash, and the CTO's portability run covers the generated ones
    (measured: exit 0, no findings).
  - Consequence: other.
  - Reversed by: an apply path that commits without the touched-hash comparison.
- **F2** (checks 1 and 2, scope out): `apply.sh` has `set -u` but not `-e`, carried over from ACT-1's F3.
  - Ordinary work: no. Consequence: other.
  - Reversed by: §5 by hand on a full or read-only disk.
- **F3** (check 1, scope out): `apply.sh`'s `rmdir .claude/templates` on undo is left over from ACT-1. It removes only
  an empty folder, and that folder holds 8 tracked files.
  - Ordinary work: no. Consequence: other.
  - Reversed by: an empty `.claude/templates/` when undo runs.
- **F4** (package text, scope out): the package said rulesync's other outputs are byte-equal to the live files. Not
  so for `.claude/settings.json`: it carries the held-out step's Read deny (DEC-616), which rulesync does not
  generate.
  - Ordinary work: yes. The builder takes only `.claude/{agents,skills,commands}`, and this ACT leaves the settings
    alone, which is right; copying the generated settings over them would drop a deny and fail open.
  - Consequence: other.
  - Reversed by: an ACT or tool that copies rulesync's `settings.json` without the held-out step.
  - The CTO corrected the package text.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": [{"id": "F2", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": []},
          {"kpi": "4", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "5", "verdict": "pass", "findings": []},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "36ab6b62950f3e26f97779d68a299e4c66b1c421438a572477a4606ec75c3fed",
 "class": "b",
 "reviewer": "independent-auditor, in-session subagent of the CTO's helper session ad44f5fe; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-10T02:13:45+00:00",
 "replay_refused": []}
```
