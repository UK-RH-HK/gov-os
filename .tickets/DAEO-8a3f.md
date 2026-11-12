---
id: DAEO-8a3f
status: in_progress
deps: []
links: [DAEO-neam, DAEO-q7lk]
created: 2026-11-11T01:20:17Z
type: task
priority: 3
assignee: engineer
external-ref: W2-158
tags: [wave-2, implementation, standard, after-the-lift, check]
wbs_id: W2-158
title: 'gov check --structural: one cheap, bounded pass over the declared check families and the new links on a head, a notice and never a refusal (EMERGENCY-TOOLS-1 D9; DEC-1052 R1-21, INVESTIGATION-1 T-2)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/check/structural.py
- src/gov/check/command.py  # the one option, --structural
- tests/unit/check/test_w2_158*
- docs/changes/W2-158-evidence.md
reads:
- src/gov/check/**
- src/gov/cli/checks.py
- src/gov/links/**
- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md
needs:
- src/gov/check/command.py
waits_on:
- ref: DAEO-q7lk
  reason: 'the links line of S4 calls `gov links --since <base>` (W2-129); this ticket skips that line while `gov links` is absent'
kpis:
  success:
  - 'S1 `gov check --structural` runs, each in a process of its own, all at once and each within a time bound (default 50 seconds, `--timeout` to change it), the tree''s declared checks of these families: schema, graph, claims, mutation, authority, pathmap, audit and skills; each command is the tree''s own declaration (template/governance/kernel/checks/<id>.yaml, else governance/kernel/checks/<id>.yaml). Verify: a planted tree with a declaration per family: eight processes started, one line per family; a stand-in command that sleeps past the bound is killed at the bound [DEC-1052, INVESTIGATION-1 T-2]'
  - 'S2 It prints one line per family: `<family>: ok`, `<family>: ok (not applicable: <reason>)`, `<family>: skipped (<reason>)` or `<family>: NOTICE <what it found, its first lines>`, then one last line `structural pass at <head12> ...`; a family that timed out is a NOTICE reading "not measured", never ok and never red. Verify: planted checks that pass, find a problem, are not applicable and time out: each reads as stated [DEC-1052, INVESTIGATION-1 T-2]'
  - 'S3 It exits 0 whatever the checks find, and 2 only when it could not run at all (no such folder, not a git work tree, bad arguments); no commit, close, landing or launch refuses or waits on its result (a landing may call it after the fact and log its lines, as the CTO''s `land.py` does). Verify: a planted failing check gives exit 0 and a NOTICE; a folder that is no work tree gives exit 2; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal [DEC-1052, DEC-1073]'
  - 'S4 With a `<base>`: the portability family runs only when `<base>..HEAD` touches template/governance/kernel/{roles,skills,hooks}/** or .rulesync/**, or when `<base>` does not resolve (otherwise it reads "skipped (no such change)"), and the tree''s own `gov links --since <base>` runs after the others, as `links: ok (0 new since <base>, M standing)` or `links: NOTICE N new: <the first finding lines>`; it writes only links'' own mark. Without a `<base>` both are left out, named. Verify: planted history with and without a kernel change; a planted tree with and without `src/gov/links/` [DEC-1052, DEC-1073]'
  - 'S5 It is bounded and cheap: the whole pass on this repository''s main tree ends within the time bound plus 10 seconds, and it reads and writes nothing else (a filesystem-spy test over a planted tree: only the declared checks'' own outputs and links'' mark). Verify: the measured time on this repository, recorded in docs/changes/W2-158-evidence.md [DEC-1052]'
  failure:
  - 'A refusal, a non-zero exit or a blocked commit, close, landing or launch because of what it found. Verify: S3''s planted failing check: exit 0 and a NOTICE line; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal'
  - 'A family that timed out reading ok or red. Verify: S1''s stand-in command that sleeps past the bound and S2''s timed-out planted check: the family''s line reads NOTICE "not measured"; a line reading ok, or a red result, is this failure'
  - 'A check run that is not the tree''s own declaration. Verify: a planted tree whose declaration for one family holds a marker command: the marker runs and no command from a built-in list does; a planted tree with no declaration for a family reads that family as skipped'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
profile: STANDARD
sources:
- DEC-1052
- DEC-1073
- DEC-1119
- DEC-1109
- DAEO-q7lk  # W2-129
- DAEO-neam  # W2-45
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W2-158/
  author: 'independent-test-designer (MR-3), from these KPI lines; planted trees with declared checks and planted histories, never this repository''s tickets'
track: C
list_rows: []
---
# W2-158 gov check --structural

Filed by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 row D9; **after the lift**, not before EXAMIN's copy (§1 D9 "no").

- **Problem.** The CTO's `structural_pass.py` (`.gov-runtime/scratch/orchestrator/tools/structural_pass.py`, R1-21, DEC-1052) gives a cheap notice-only pass over the check families after every record commit and every landing. Its own docstring says "later replaced by T-2's `--families`", but no ticket holds T-2's scoped check: W2-45 (runner semantics) lists no scoped or notice-only run, and `gov check` has only `--list`. An adopted product has the 17 families and no cheap way to run them after a commit.
- **Approach.** A module that reads the declarations the runner already reads, starts each in its own process with a bound, and prints the notice lines. It reuses the declarations; it adds no check. Alternatives: `gov check --changed <base>` with input globs per check (INVESTIGATION-1 T-2's full design, left to W2-45 or a later ticket); a wrapper script in the template (rejected: scratch tools are the problem this audit names).
- **Interface.** `gov check --structural [<base>] [--timeout <s>]`; the output lines as S2; exit codes as S3.
- **Non-goals.** No new check, no scoping by input globs, no gate; W2-45's runner semantics are untouched.
- **Rabbit holes.** Making a notice a refusal (never, DEC-1052); running the checks in sequence (one process each, all at once, is the measured speed).

[DEC-1052, DEC-1073, DEC-1119 (5)]
