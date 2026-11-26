---
id: DAEO-stdl
status: in_progress
deps: []
links: []
created: 2026-11-26T11:30:00Z
type: task
priority: 2
assignee: engineer
external-ref: W2-213
tags: [layout, classification, rubric, path-map, adoption, imports, kit]
wbs_id: W2-213
title: "A standard repository layout and classification by rubric: the path map follows a standard, never words in paths; agents class in parallel in a fixed form, code merges and checks, the owner approves an owned repository's moves, code executes and rolls back"
class: implementation
kind: feature
approved_by: [DEC-1255, DEC-1256]
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: []
waits_on: []
specification: docs/specs/W2-213-standard-layout.md
allowed_paths:
- docs/specs/W2-213-standard-layout.md
- template/governance/kernel/standard.yaml
- template/governance/kernel/schemas/standard.schema.json
- src/gov/layout/**
- src/gov/check/commands.py
- src/gov/adopt/fabric.py
- src/gov/_shipped/**
- pyproject.toml
- governance/project/path-map.yaml
- tests/unit/layout/**
- tests/unit/adopt/test_w2_88_shipped.py
- tests/acceptance/W2-213/**
- tests/acceptance/W1-32/test_w1_32_command_set.py
kpis:
  success:
  - line: 'SL-1 The kit holds one standard file with a closed list of exactly eighteen classes (code, tests, spec, research, docs, record, governance, kit, config, data, generated, archive, import-use, import-absorb, import-study, evaluation, hidden-set, secret), one entry each, giving its destination, whether it ever moves, its memory policy and ranking tier, and the signs it is told by, as the rubric''s class table states them, and holds the ask answer apart as no class.'
    verify: 'the committed `template/governance/kernel/standard.yaml` is read and its `classes` entries compared, id by id, with rubric §1''s table (destination, `moves`, memory policy, tier, signs); the product is the list of eighteen ids equal to it, `ask` outside it.'
  - line: 'SL-2 The same standard file holds the layout and its rules: every folder of the standard; the three archive sub-folders, each with its stale class, and no stale class anywhere else; the tool-fixed paths that never move, each with its class; the rules that code and tests keep their native layout and that an import moves whole with one class; the name patterns of secret and generated roots; the study ceiling of 2,000 chunks an import and 5,000 a repository; the tool-written record folders; and which file kinds count as documents.'
    verify: 'the same file''s layout entries compared with rubric §2''s tree, L1 to L6, §1''s secret and generated patterns, M2''s stale classes and the study ceiling; the product is, for a planted path of each class, the destination derived from the file alone.'
  - line: 'SL-3 The standard has a published schema and a version: the committed standard is valid, and a copy with an unknown or missing class, a missing destination or memory policy, a stale class outside the archive, an unknown policy value or an unknown key is refused, naming the fault.'
    verify: '`check-jsonschema` with `standard.schema.json` accepts the committed file and refuses each faulty copy, its output naming the faulty key; the file holds a `version`.'
  - line: 'SL-4 An adopted repository receives the standard with the kit at its next update and a changed copy there shows as drift; the check run from the Gov OS source tree or from an installed release finds the shipped standard in a repository that does not yet hold the kit''s copy, and never works with a standard of its own in code.'
    verify: 'in a planted adopted project, `gov update` to a release holding the file leaves `governance/kernel/standard.yaml` listed in `framework.lock`; an edit makes `gov doctor` report lock drift; with the project''s copy removed from a repository, `gov layout check` from the source tree and from the installed package copy still runs; with every shipped copy absent it refuses naming the file.'
  - line: 'SL-5 One command, the layout check, reads a plan file of one answer per line with exactly the nine fields path, class, destination, reason, kind, stale class, import name, sign and ask (a field that does not apply is written empty; the chunk and agent of a line may be added and change no result), checks it against the repository''s committed files, its untracked and ignored items and the declared lines of its import register, prints each finding with its kind, the plan line number and the path, and ends clean only when there is no finding; it ends with one of three distinct results (clean, findings, cannot run) and writes nothing.'
    verify: '`gov layout check <plan> --root <planted repo> --json` on the clean plan gives exit 0 and an envelope with no findings; each faulty plan gives exit 1 and a finding holding code, line and path; an unreadable plan, a broken standard, a non-repository and a modified tracked file each give exit 2 with `LAYOUT_CANNOT_RUN`; `git status --porcelain` and HEAD are unchanged after every run.'
  - line: 'SL-6 The check never opens a file that is registered as a hidden evaluation set or that carries a secret file name, and no output of it holds any byte of such a file or of a secret it finds elsewhere; it names the path, and for a content finding the rule, only.'
    verify: 'the planted hidden-set and secret-named files are made unreadable and the run gives the same result; the printed text and the envelope hold the paths and the filter''s rule id and none of the planted sentinels.'
  - line: 'SL-7 Exactly once: every tracked file, every untracked file git does not ignore, every ignored root as one item, every submodule and every declared line of the import register is covered by exactly one plan line, after folder lines are expanded; a gap and a double are each a finding naming the path, and a gap that a rule decides alone says which class the rule gives it.'
    verify: 'plans with one line removed, one line doubled, a file line under a folder line, an extra line naming nothing, and a kit file classed as docs give `LAYOUT_GAP`, `LAYOUT_DOUBLE`, `LAYOUT_DOUBLE`, `LAYOUT_NO_ITEM` and `LAYOUT_RULE_CLASS`; an empty plan lists every item once, each rule-decided one with its class.'
  - line: 'SL-8 Valid: a line with a class outside the closed list (ask apart), a missing or unknown field, a kind or sign outside their lists or a kind that does not match the item, a stale class missing for archive or present elsewhere or not one of the three, an import name missing for an import class or present elsewhere, an ask line without a question and a recommended class or an ask value on another class, an empty reason, or one reason copied across more than ten paths is a finding naming that fault.'
    verify: 'one planted line per fault listed gives `LAYOUT_INVALID` naming the field; ten identical reasons pass and an eleventh gives the finding.'
  - line: 'SL-9 Where the standard puts it: each line''s destination equals the one place the standard gives its class, path and import name; an item that never moves (a tool-fixed path, anything under a manifest''s package root, code, tests, the kit, config, governance, evaluation, hidden-set, secret, generated, ignored and ask items) has its own path as destination, and a different destination is a finding that states the expected one.'
    verify: 'planted wrong destinations for each class, a moved tool-fixed file, a moved test and a moved file under the manifest''s package root give `LAYOUT_DESTINATION` with the expected path; the clean plan''s destinations of every class give none.'
  - line: 'SL-10 Coherent: two lines of one import with different import classes, an import whose lines would move it other than whole, two items with one destination, a destination that already exists in the repository, each is a finding naming both paths; a hidden-set path found inside the tree and a tracked secret (by its name pattern, by its line''s class or by the repository''s secrets filter) are each reported at once as a stopper and the plan is not clean.'
    verify: 'planted mixed import classes and a split import give `LAYOUT_IMPORT`; a shared and an existing destination give `LAYOUT_TARGET_TAKEN`; the planted hidden-set path, a tracked secret by name, by class and by content give `LAYOUT_STOPPER` with exit 1; the ignored secret file gives none.'
  - line: 'SL-11 References: for every item the plan moves, the check lists every tracked file that names its path or links to it, and the relative links a moving document holds; a mention in a document is listed as a rewrite, a mention in code, tests or configuration holds the item, which is named as held, and a mention in the path map, the kit, an import''s own files, a generated file or a tool-written record is listed as kept; rewrites, holds and kept mentions are reported without making the plan unclean.'
    verify: 'the envelope''s `rewrites`, `held` and `kept` lists equal the planted references: a Markdown link, a front-matter path and a moving document''s relative link under `rewrites`; the code and configuration mentions holding their item under `held`; a path-map and a tool-written record mention under `kept`; exit 0 on the otherwise clean plan.'
  - line: 'SL-12 The map compiles: the namespaces the standard and the plan imply place every destination in exactly one namespace (one per class, three for the archive, two for study imports, one per import); two classes claiming one destination or a folder line holding another class''s destination is a finding; each archive namespace carries its stale class with both policies out; a study import within the ceiling is placed under meaning search and one over it under keyword search, with its chunk count stated.'
    verify: 'planted overlapping destinations give `LAYOUT_MAP`; the envelope names each namespace with its policies and each study import''s chunk count and namespace, the one over the ceiling under keyword search.'
  - line: 'SL-13 Deterministic and ready to show the owner: the same plan lines in any order, the same standard version and the same commit give the same output byte for byte and the same recorded plan hash, and a changed line, standard or commit changes the hash; the output states the standard''s version, the commit, the number of items per class, every ask line with its question, every rewrite, every held item and every stopper.'
    verify: 'the clean plan run twice and with its lines shuffled gives identical bytes and `hash`; changing one reason, the standard''s version or the commit changes `hash`; counts, asks, rewrites, holds and stoppers equal the planted ones.'
  - line: 'SL-14 After the moves: asked to check a moved repository against the same plan, the check is clean only when every moving item that is not held is at its destination and gone from its old path, every held, ask and never-moving item is where it was, no tracked or untracked item is outside the plan, no listed rewrite still names an old path, and the repository''s own path map places every tracked path in exactly one namespace with the memory policy and stale class the standard gives its class.'
    verify: '`gov layout check <plan> --moved` on the correctly moved copy gives exit 0; each planted after-move fault gives `LAYOUT_MOVE` or `LAYOUT_MAP` naming the path.'
  failure:
  - 'F-SL1 a class is missing, extra or listed twice, ask appears among the classes, or an entry''s destination, move rule, memory policy or tier differs from the accepted rubric.'
  - 'F-SL2 a folder, a tool-fixed path, a secret or generated name pattern, a tool-written folder or a ceiling that the rubric states is absent or different, or the destination of some class and path cannot be worked out from the standard alone.'
  - 'F-SL3 the committed standard is refused, or any one of the faulty copies is accepted.'
  - 'F-SL4 an updated repository lacks the file, a changed copy passes unnoticed, the check cannot run in a repository without the copy, or a missing standard is replaced by a default.'
  - 'F-SL5 a plan with a finding ends clean, a finding lacks its line number or path, an unreadable plan, standard or repository or uncommitted change to a tracked file ends as clean or as findings, or any file of the repository or its history changes during a run.'
  - 'F-SL6 a planted hidden-set or secret-named file is opened, or any planted content or secret value appears on the screen, in the structured output or in any file.'
  - 'F-SL7 an uncovered item, an item covered twice or a file line below a folder line passes, a line naming nothing in the repository passes, or a rule-decided item is accepted under another class.'
  - 'F-SL8 any one of these planted lines passes, or a valid line is reported.'
  - 'F-SL9 a wrong destination passes, a move of a tool-fixed path, of code or a test or of anything under a native package root passes, or a correct destination is reported.'
  - 'F-SL10 any of these passes, a stopper is reported as an ordinary finding or left out, or a planted ignored secret file is called a stopper.'
  - 'F-SL11 a planted document mention, code mention, relative link or front-matter path is missing or listed under another outcome, or a held item is shown as moving.'
  - 'F-SL12 an overlapping pair passes, an archive namespace lacks a policy, or a study import over either ceiling is placed under meaning search.'
  - 'F-SL13 two runs on the same inputs differ, a changed input keeps the hash, or a count, ask line, rewrite, hold or stopper is missing or wrong.'
  - 'F-SL14 a planted unmoved item, moved held item, unrewritten reference, unplanned new file or a namespace with a wrong policy passes, or a correctly moved repository is not clean.'
non_goals:
- Restructuring Gov OS itself (it keeps its classing until restructuring pays; its tests pin its paths)
- Restructuring an imported tool or code (it sits whole in imports/<name>/ with one class)
- Slice 1 moves, rewrites, generates and rebuilds nothing by code, and classes nothing by code beyond what a rule decides (slices 2 to 4 are the products' work; the rest is slice 5)
sources: [docs/specs/W2-213-standard-layout.md, DEC-1256, DEC-1255, DEC-1254, DEC-1222, DEC-1228, DEC-1252, docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md]
acceptance_tests:
  path: tests/acceptance/W2-213/
  author: independent-test-designer (MR-3); written before implementation, from the specification
track: F
---
# W2-213: a standard repository layout and classification by rubric

Approved as a feature by the owner on 2026-11-26 (DEC-1255 (2)); the integration plan's F-5. The rubric was accepted the same day
(DEC-1256) and the specification is written: `docs/specs/W2-213-standard-layout.md`. **Ready for slice 1** (SL-1 to SL-14: the
standard frozen in the kit and the layout check), built first, in the owner's order (DEC-1256 (1)), and shipped to EXAMIN and ASMO OS
by the next release or by hand if sooner. Slices 2 to 4 are the products' work; slice 5, drafted in the spec, gets its K-lines when
slice 1 lands.

## The owner's scope (DEC-1255 (2), his words in short)
- **The standard, in the kit:** where code, tests, specs (`docs/specs`), research (`docs/research`), governance, everything stale (one
  `archive/` folder) and everything a repository brings in (`imports/<name>/`) live; the path map's namespaces and classes fixed by it.
- **Owned repositories** (EXAMIN, ASMO OS) are restructured to the standard at adoption's A6, with the owner's yes on the moves; their
  path map then follows the standard. **A new repository** starts in it: `gov init` (I-25). **An import** (REA, Startup Launchpad, a
  library) is never restructured: whole in `imports/<name>/`, one class (use, absorb or study). **Gov OS** keeps its classing for now.
- **How:** the rubric becomes code (classes, rules, where each class lives); agents class each file, folder and piece of material in a
  fixed form (path, class, destination, reason), over disjoint chunks by path, up to ten in parallel within the machine's gate; code
  merges and checks (every tracked file classed exactly once, every class valid, every destination where the standard puts it; a gap, a
  double or a conflict back to its agent); the orchestrator reviews the merged classification and the restructuring plan and brings the
  owner an owned repository's moves; code executes the approved plan (moves, path map regenerated from the standard, memory rebuilt, the
  impact-selected tests, rollback on any break). The same flow for adoption, an import, installing a tool, testing a tool before use,
  and retiring.

## Why
D3's adoption check guessed staleness from words in paths (I-40, DEC-1254 E-02): every guess needs a new exception; a standard does not.
