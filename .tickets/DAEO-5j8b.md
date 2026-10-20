---
id: DAEO-5j8b
status: in_progress
deps: []
links: []
created: 2026-10-20T07:08:28Z
type: task
priority: 1
assignee: engineer
external-ref: W2-58
tags: [wave-2, implementation, standard]
wbs_id: W2-58
title: 'Policy 2 in the guard and the launcher: reads open, four refusals'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/guard/protected.py
- src/gov/guard/heldout.py
- src/gov/guard/decide.py
- src/gov/guard/reads.py
- src/gov/launch/**
- governance/project/path-map.yaml
- template/governance/kernel/schemas/path-map.schema.json
- tests/unit/guard/**
- tests/unit/launch/**
- docs/changes/W2-58-CIT-E.md
kpis:
  success:
  - A session of role engineer on ticket T is refused reads of tests/acceptance/<T's W2 id>/** by the guard, on every tool read and the read side of every Bash route an honest agent takes (no OS-level Read rule for it, DEC-873), and can still run those tests with pytest and see their names, results and failure messages [DEC-820 (c)].
  - 'The launcher adds no OS-level Read deny rule for (c) or (d), because running a test means reading it; the held-out material''s Read rules (b) stay in the sandbox; a launch under a malformed evaluation_sets block is refused [DEC-873]'
  - A session of role independent-test-designer on T is refused reads of the files T's branch changes against its base, other than its own tests, and reads the base's version of existing code [DEC-820 (c), DEC-826 Q2].
  - An evaluation set declared in the path map with a visible and a hidden part, a session measured by it is refused reads of the hidden part, and the measurement script scores it without showing the answers [DEC-820 (d)].
  - 'The listing and search refusals over governance/ and .claude/ (DEC-508) are gone: a search that starts at the repository root or governance/project/ is no longer refused for the protected files'' sake; the held-out list file''s names are readable and the held-out material''s contents refused; the settings file''s reads follow Policy 2; secrets stay refused [DEC-820 (a), (b), DEC-857 item 3]'
  - Reviewers and auditors read everything, tests and code alike [DEC-820].
  failure:
  - Each of (a) to (d) still refuses, by every read route an honest agent takes in ordinary work (DEC-801); no write rule widens; a guard error still fails closed.
profile: STANDARD
sources:
- DEC-820
- DEC-821
- DEC-849
- DEC-857
- DEC-873
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-58/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- DEC-820
- DEC-821
list_rows: []
---
# W2-58 Policy 2 in the guard and the launcher: reads open, four refusals

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-58), from DEC-820 and DEC-821 (owner, 2026-10-19; the guard and launcher change is approved there, CAP-33) and DEC-857 (owner, 2026-10-19: straight after W2-50 merges, ahead of every other start, and widened to the two files the guard protects by constant).

- **Why:** Policy 2 opens reads to everything but four things: (a) secrets, (b) the held-out material's contents, (c) the counterpart's work on the same ticket, (d) the hidden half of an evaluation set. The guard still refuses reads Policy 2 opened: any target that takes in `governance/project/held-out.yaml` or `.claude/settings.json` (the constants in `src/gov/guard/heldout.py:19-21`, the rule in `src/gov/guard/protected.py`), so a search from the repository root or `governance/project/` is refused. No setting changes this (DEC-857 item 2). It also lacks (c) and (d).
- **Allowed paths:** `src/gov/guard/protected.py`, `src/gov/guard/heldout.py`, `src/gov/guard/decide.py` (the read rules only), `src/gov/guard/reads.py` (new, if the read rules need a module of their own), `src/gov/launch/**` (the sandbox's read denials only), `governance/project/path-map.yaml` (an `evaluation_sets` block only, reviewed by the orchestrator, DEC-861), `template/governance/kernel/schemas/path-map.schema.json` (the same block), `tests/unit/guard/**`, `tests/unit/launch/**`, `docs/changes/W2-58-CIT-E.md`. **Not** `src/gov/guard/containment.py`: W2-05's unmerged branch changes it; a need there is a package.
- **KPIs, success:**
  - A session of role `engineer` on ticket T is refused reads of `tests/acceptance/<T's W2 id>/**` by the guard, on every tool read and the read side of every Bash route an honest agent takes (no OS-level Read rule for it, DEC-873), and can still run those tests with pytest and see their names, results and failure messages [DEC-820 (c)].
  - **DEC-873 (owner, 2026-10-20, P-W2-58-1 (a)):** the launcher adds no OS-level Read deny rule for (c) or (d), because running a test means reading it; the held-out material's Read rules (b) stay in the sandbox; a launch under a malformed `evaluation_sets` block is refused. A program run deliberately to evade the guard is Wave 3 row W2-L374.
  - A session of role `independent-test-designer` on T is refused reads of the files T's branch changes against its base, other than its own tests, and reads the base's version of existing code [DEC-820 (c), DEC-826 Q2].
  - An evaluation set declared in the path map with a visible and a hidden part: a session measured by it is refused reads of the hidden part, and the measurement script scores it without showing the answers [DEC-820 (d)].
  - The listing and search refusals over `governance/` and `.claude/` (DEC-508) are gone: a search that starts at the repository root or `governance/project/` is no longer refused for the protected files' sake; the held-out list file's names are readable and the held-out material's contents refused; the settings file's reads follow Policy 2; secrets stay refused [DEC-820 (a), (b), DEC-857 item 3].
  - Reviewers and auditors read everything, tests and code alike [DEC-820].
- **KPIs, failure:** each of (a) to (d) still refuses, by every read route an honest agent takes in ordinary work (DEC-801); no write rule widens; a guard error still fails closed.
