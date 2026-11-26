# W2-213: a standard repository layout and classification by rubric

Ticket `DAEO-stdl` (W2-213), `kind: feature`. Source: the classification rubric
`docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md`, accepted by DEC-1256 (page B-2026-11-26-rubric: R-01 to R-12,
C-01 to C-05, with C-03 (c)), under DEC-1255. "Rubric §n", "R-nn", "L-n" and "M-n" point into the rubric. Written in the
owner's order (DEC-1256 (1) to (5)): **slice 1** is specified here in full and ready to build; slices 2 to 4 are the flow
it must serve; **slice 5** is drafted and is finalised when slice 1 lands. Where this file and the rubric differ, the
rubric holds and the difference is a defect of this file.

## Problem

Each repository keeps its own folders and its own path map, so memory cannot tell what is current from what is stale
without guessing from words in paths, which failed both ways (I-40). The owner accepted one standard layout with a closed
list of classes, and ordered that EXAMIN and ASMO OS restructure to it once, by hand, with no second pass. That is safe
only if the standard is frozen first and a repository's plan can be checked by code before anything moves: a wrong
restructure now would break every release after it (DEC-1256).

## Users and scenarios

- A product's CTO classes the repository in chunks with Sonnet helpers, joins their answers into one plan, and runs the
  layout check until it is clean; the findings name each wrong line, so the chunk's agent can correct it.
- The same CTO runs the check on a half-written plan; it names every item not yet covered, and says which of them a rule
  already classes, so those lines are written by the CTO and never handed to an agent to read.
- The owner receives one plan to say yes to, with the counts per class, every question, every reference to be rewritten
  and every move held back.
- The CTO moves the files by hand on the owner's yes, rewrites the references, writes the new path map from the standard,
  rebuilds memory, runs the selected tests and runs the check again; anything red rolls back.
- A product that has not taken a release yet runs the check from the Gov OS source tree against its own repository.

## Goals

- One standard, frozen in the kit: the folders, the classes, where each class lives and what memory holds of it.
- A plan form of nine fields that agents write and code reads.
- A check that runs the seven code checks of R-09 on a plan before any move, writes nothing, and says clean only when the
  plan is clean.
- The same check usable after the hand moves, so a restructure can be proven or rolled back.

## Non-goals

- Moving, renaming, rewriting or deleting any file by code; generating a path map; rebuilding memory (slice 5).
- Splitting a repository into chunks, starting agents or merging their answers by code (slice 5).
- Deciding an item's class: that stays an agent's judgement inside the fixed form (rubric §6).
- Finding references that code builds at run time (a path joined from parts); the selected tests catch those and the
  restructure rolls back.
- Retiring the word check of D3, or changing the record graph, the indexes or ranking (slice 5; rubric §3, §8).
- Restructuring Gov OS, or restructuring inside an import (R-07, L5, C-04).

## KPIs

- K1: SL-1 The kit holds one standard file with a closed list of exactly eighteen classes (code, tests, spec, research, docs, record, governance, kit, config, data, generated, archive, import-use, import-absorb, import-study, evaluation, hidden-set, secret), one entry each, giving its destination, whether it ever moves, its memory policy and ranking tier, and the signs it is told by, as the rubric's class table states them, and holds the ask answer apart as no class.
  Fails if: a class is missing, extra or listed twice, ask appears among the classes, or an entry's destination, move rule, memory policy or tier differs from the accepted rubric.
- K2: SL-2 The same standard file holds the layout and its rules: every folder of the standard; the three archive sub-folders, each with its stale class, and no stale class anywhere else; the tool-fixed paths that never move, each with its class; the rules that code and tests keep their native layout and that an import moves whole with one class; the name patterns of secret and generated roots; the study ceiling of 2,000 chunks an import and 5,000 a repository; the tool-written record folders; and which file kinds count as documents.
  Fails if: a folder, a tool-fixed path, a secret or generated name pattern, a tool-written folder or a ceiling that the rubric states is absent or different, or the destination of some class and path cannot be worked out from the standard alone.
- K3: SL-3 The standard has a published schema and a version: the committed standard is valid, and a copy with an unknown or missing class, a missing destination or memory policy, a stale class outside the archive, an unknown policy value or an unknown key is refused, naming the fault.
  Fails if: the committed standard is refused, or any one of the faulty copies is accepted.
- K4: SL-4 An adopted repository receives the standard with the kit at its next update and a changed copy there shows as drift; the check run from the Gov OS source tree or from an installed release finds the shipped standard in a repository that does not yet hold the kit's copy, and never works with a standard of its own in code.
  Fails if: an updated repository lacks the file, a changed copy passes unnoticed, the check cannot run in a repository without the copy, or a missing standard is replaced by a default.
- K5: SL-5 One command, the layout check, reads a plan file of one answer per line with exactly the nine fields path, class, destination, reason, kind, stale class, import name, sign and ask (a field that does not apply is written empty; the chunk and agent of a line may be added and change no result), checks it against the repository's committed files, its untracked and ignored items and the declared lines of its import register, prints each finding with its kind, the plan line number and the path, and ends clean only when there is no finding; it ends with one of three distinct results (clean, findings, cannot run) and writes nothing.
  Fails if: a plan with a finding ends clean, a finding lacks its line number or path, an unreadable plan, standard or repository or uncommitted change to a tracked file ends as clean or as findings, or any file of the repository or its history changes during a run.
- K6: SL-6 The check never opens a file that is registered as a hidden evaluation set or that carries a secret file name, and no output of it holds any byte of such a file or of a secret it finds elsewhere; it names the path, and for a content finding the rule, only.
  Fails if: a planted hidden-set or secret-named file is opened, or any planted content or secret value appears on the screen, in the structured output or in any file.
- K7: SL-7 Exactly once: every tracked file, every untracked file git does not ignore, every ignored root as one item, every submodule and every declared line of the import register is covered by exactly one plan line, after folder lines are expanded; a gap and a double are each a finding naming the path, and a gap that a rule decides alone says which class the rule gives it.
  Fails if: an uncovered item, an item covered twice or a file line below a folder line passes, a line naming nothing in the repository passes, or a rule-decided item is accepted under another class.
- K8: SL-8 Valid: a line with a class outside the closed list (ask apart), a missing or unknown field, a kind or sign outside their lists or a kind that does not match the item, a stale class missing for archive or present elsewhere or not one of the three, an import name missing for an import class or present elsewhere, an ask line without a question and a recommended class or an ask value on another class, an empty reason, or one reason copied across more than ten paths is a finding naming that fault.
  Fails if: any one of these planted lines passes, or a valid line is reported.
- K9: SL-9 Where the standard puts it: each line's destination equals the one place the standard gives its class, path and import name; an item that never moves (a tool-fixed path, anything under a manifest's package root, code, tests, the kit, config, governance, evaluation, hidden-set, secret, generated, ignored and ask items) has its own path as destination, and a different destination is a finding that states the expected one.
  Fails if: a wrong destination passes, a move of a tool-fixed path, of code or a test or of anything under a native package root passes, or a correct destination is reported.
- K10: SL-10 Coherent: two lines of one import with different import classes, an import whose lines would move it other than whole, two items with one destination, a destination that already exists in the repository, each is a finding naming both paths; a hidden-set path found inside the tree and a tracked secret (by its name pattern, by its line's class or by the repository's secrets filter) are each reported at once as a stopper and the plan is not clean.
  Fails if: any of these passes, a stopper is reported as an ordinary finding or left out, or a planted ignored secret file is called a stopper.
- K11: SL-11 References: for every item the plan moves, the check lists every tracked file that names its path or links to it, and the relative links a moving document holds; a mention in a document is listed as a rewrite, a mention in code, tests or configuration holds the item, which is named as held, and a mention in the path map, the kit, an import's own files, a generated file or a tool-written record is listed as kept; rewrites, holds and kept mentions are reported without making the plan unclean.
  Fails if: a planted document mention, code mention, relative link or front-matter path is missing or listed under another outcome, or a held item is shown as moving.
- K12: SL-12 The map compiles: the namespaces the standard and the plan imply place every destination in exactly one namespace (one per class, three for the archive, two for study imports, one per import); two classes claiming one destination or a folder line holding another class's destination is a finding; each archive namespace carries its stale class with both policies out; a study import within the ceiling is placed under meaning search and one over it under keyword search, with its chunk count stated.
  Fails if: an overlapping pair passes, an archive namespace lacks a policy, or a study import over either ceiling is placed under meaning search.
- K13: SL-13 Deterministic and ready to show the owner: the same plan lines in any order, the same standard version and the same commit give the same output byte for byte and the same recorded plan hash, and a changed line, standard or commit changes the hash; the output states the standard's version, the commit, the number of items per class, every ask line with its question, every rewrite, every held item and every stopper.
  Fails if: two runs on the same inputs differ, a changed input keeps the hash, or a count, ask line, rewrite, hold or stopper is missing or wrong.
- K14: SL-14 After the moves: asked to check a moved repository against the same plan, the check is clean only when every moving item that is not held is at its destination and gone from its old path, every held, ask and never-moving item is where it was, no tracked or untracked item is outside the plan, no listed rewrite still names an old path, and the repository's own path map places every tracked path in exactly one namespace with the memory policy and stale class the standard gives its class.
  Fails if: a planted unmoved item, moved held item, unrewritten reference, unplanned new file or a namespace with a wrong policy passes, or a correctly moved repository is not clean.

## Test data

| source | kind | owner | licence or recipe | privacy | secrets | hidden half | secured |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A planted owned repository holding material of every class and kind: a manifest with a package root and its tests, a spec, a study, current and dated documents, a retired system, tool-fixed files, the kit's copy, own synthetic data, a tracked generated file and ignored generated roots, an untracked folder, a submodule entry, a declared register line, use, absorb and study imports (a study one under the ceiling and one over it), a vendored library, an evaluation set, a registered hidden-set path with sentinel content, an ignored secret file and a tracked fake secret, and a moving document named by a document link, by front matter, by code and by configuration | synthetic | independent test designer | built at test time from a fixed seed, file by file and commit by commit, never committed; every name and text invented | none | fake secrets assembled from parts at test time inside the temporary repository only, never written whole in a tracked file | n/a | yes |
| Synthetic plans for that repository: one clean plan, one faulty plan for each finding of the seven checks, the same lines in two orders, and a moved copy of the repository with one planted fault per after-move finding | synthetic | independent test designer | derived by code from the planted repository's own item list and the standard, one planted fault per plan | none | none | n/a | yes |
| Faulty copies of the standard file, one fault each | synthetic | independent test designer | the committed standard changed by one named fault each at test time | none | none | n/a | yes |

## Out of scope

- Slices 2 to 4, the products' own work by the rubric (below): each product's CTO and the owner.
- Slice 5, the rest of W2-213 (below): this ticket, once slice 1 has landed.
- The adopt skill and other kernel text that would name the check: the CTO's change (EMERGENCY-2 3.5), after the build.
- The imports feature's register and stage: its own ticket (DEC-1228 (1)); slice 1 only reads the register's lines.
- Adding the specs folder to the governing ranking tier in Gov OS's path map: Gov OS keeps its classing (C-04); a CTO chore
  if memory should rank it.

## Open questions

Each has a default that the K-lines above already follow, so the build does not wait; a different answer changes the
named lines.

- Question: Where does the standard file live? The rubric's §2 writes it directly under the kit's governance folder and calls it a kernel file; only the kernel folder is locked, released and compared as drift. (SL-4)
  - Options: in the kernel folder beside the other kernel files (cost: differs from the path written in §2); at the path §2 writes (cost: the release lock, the drift check and both path maps must each be widened)
  - Recommendation: in the kernel folder, because R-04 asks for a kit file that an update carries and §2 calls it a kernel file.
- Question: What is the destination for the classes L1 leaves open (docs, data), for the folder name inside the research and record places, and for a file already in an old archive folder? (SL-9)
  - Options: an item already inside its class's place stays; a docs or data item outside it goes to the docs or data folder under its own file or folder name; research and records take one folder of the agent's choosing followed by the file name; an old archive file drops its leading archive segment before it goes under the stale class (cost: two agents may name a record kind differently; the orchestrator's review sees it); a closed list of record kinds in the standard (cost: the owner's yes for each new kind); keep the whole old path under docs or data (cost: deep paths, and a rubric that says file name for research and records)
  - Recommendation: the first, as the smallest rule code can check.
- Question: The rubric's example line carries the chunk and the agent besides the nine fields. Are they allowed? (SL-5)
  - Options: allowed as two optional provenance keys that no check judges (cost: a line may hold eleven keys); refused, with provenance in each chunk's file name (cost: a failed line can no longer be traced to its agent after the merge)
  - Recommendation: allowed, since a failing line goes back to its chunk's agent.
- Question: L4 lists every tracked file that names a moving path. What of mentions in the path map, the kit, imports, generated files and tool-written records, which are neither rewritten by hand nor a reason to hold a move? (SL-11)
  - Options: listed as kept, neither rewritten nor holding (cost: an old path stays in a dated record, as history); treated by file kind alone, document or code (cost: tool-written records and the path map would hold most moves)
  - Recommendation: listed as kept.
- Question: The owner's order runs the check again after the moves, but R-09's checks read a plan before any move. Is the after-move mode part of slice 1? (SL-14)
  - Options: yes, in slice 1 (cost: one more K-line and its tests); in slice 5, with the products writing a second plan of the moved tree by hand to re-run the check (cost: a second classing pass under the one-restructure rule, and nothing proves the moves match the approved plan)
  - Recommendation: yes: step 3 of the order cannot be met without it.
- Question: How does the check find a tracked secret that has an ordinary name? (SL-10)
  - Options: by name pattern, by class and by the repository's existing secrets filter, naming the rule only (cost: seconds to minutes a run; nothing is found where the filter is switched off, and the output says so); by name and class only (cost: an agent may be handed the file)
  - Recommendation: with the filter, as rubric §4 keeps flagged files from every agent.
- Question: The import register is not built yet. What does the check read from it? (SL-7)
  - Options: the path of each entry of the register's list of imports where the file exists, refusing to run on a file it cannot read (cost: the imports feature keeps that shape); ignore the register in slice 1 (cost: declared material outside the tree can be missed)
  - Recommendation: read the paths.

## Accepted by

The owner has accepted the rubric this spec is written from (DEC-1256); the CTO accepts this spec and its K-lines when it
lands on the integration branch. Each K-line is then accepted by the independent test designer's tests, red on the base,
and a green `gov accept W2-213`; slice 1 is done when EXAMIN's and ASMO OS's CTOs can run the check on their plans.

## Slice 1: where it lives (for the builder; names code)

| What | Where |
|---|---|
| The standard | `template/governance/kernel/standard.yaml`, copied byte for byte to `src/gov/_shipped/template/governance/kernel/standard.yaml`, named in `fabric.PACKAGED` and `pyproject.toml`'s package data; read only through `gov.adopt.fabric.shipped` |
| Its schema | `template/governance/kernel/schemas/standard.schema.json` (JSON Schema 2020-12). A new schema file means no patch release carries it (rule P5) |
| The checker | `gov layout check <plan> [--moved] [--root <path>] [--json]`, module `src/gov/layout/command.py` (`CLASS` read, `CHILD_EXIT_CODE`), recorded in `src/gov/check/commands.py` and in W1-32's command set |
| Exit codes | 0 clean; 1 findings or stoppers; 2 cannot run (`LAYOUT_CANNOT_RUN`) |
| Finding codes | `LAYOUT_GAP`, `LAYOUT_DOUBLE`, `LAYOUT_NO_ITEM`, `LAYOUT_RULE_CLASS`, `LAYOUT_INVALID`, `LAYOUT_DESTINATION`, `LAYOUT_IMPORT`, `LAYOUT_TARGET_TAKEN`, `LAYOUT_STOPPER`, `LAYOUT_MAP`, `LAYOUT_MOVE` |
| A finding's line | `gov layout check: <CODE> line <n or ->: <path>: <message>`; notices are `REWRITE`, `HELD`, `KEPT` and `ASK` in the same form |
| `--json` | the shared envelope, `result` holding `findings`, `rewrites`, `held`, `kept`, `asks`, `stoppers`, `counts`, `commit`, `standard`, `hash` |

**The plan's file form.** UTF-8 JSON Lines: one JSON object a line, blank lines skipped, line numbers those of the file.
Keys, all present on every line, `null` where they do not apply: `path`, `class`, `destination`, `reason`, `kind`,
`stale_class`, `import`, `sign`, `ask`; optionally `chunk` and `agent`. `class` is one of the eighteen or `ask`; `kind`
is `file`, `folder`, `untracked`, `ignored-root`, `submodule` or `declared`; `stale_class` is `superseded`, `historical`
or `legacy`; `sign` is `path`, `manifest`, `licence`, `header`, `front-matter`, `history`, `imports`, `content` or
`registry`; `ask` is `null` or `{"question", "recommended"}`. Paths are repository-relative with `/`, folders without a
trailing slash; a `folder` or `untracked` line covers everything below it. Chunk answers are merged by concatenating them.

```json
{"path": "docs/plans/roadmap-2025.md", "kind": "file", "class": "archive", "stale_class": "superseded", "import": null, "destination": "archive/superseded/docs/plans/roadmap-2025.md", "reason": "front matter status SUPERSEDED, superseded_by docs/plans/roadmap-2026.md", "sign": "front-matter", "ask": null, "chunk": "c03", "agent": "<session id>"}
```

**Where a plan lives.** `governance/adoption/layout-plan.jsonl` in the repository being restructured (an adoption
record), though the check takes any path. The file given to the check is never one of the plan's items.

**Inputs the check reads.** The shipped standard; the commit at HEAD; `git ls-files` with its untracked, ignored and
submodule entries; the committed path map's `evaluation_sets` hidden globs and `sets_root_hidden` hidden globs; the
manifests that name a package root; `governance/project/imports.yaml` (the entries under `imports:`, their `path`); the
contents of tracked files for references and secrets, never of a hidden-set or secret-named file. It refuses to run on
uncommitted changes to tracked files.

## The flow slice 1 must serve (slices 2 to 4; not this ticket's code)

| Slice | Who | The flow | What it needs from slice 1 |
|---|---|---|---|
| 2: class and approve | each product's CTO, then the owner | Splits the items into disjoint chunks by path, up to ten within the machine's gate (R-08); Sonnet helpers write nine-field lines; `ask` where unsure (R-10); the CTO concatenates them, runs the check until clean (a failing line goes back to its chunk's agent at most twice, then to the CTO) and brings the owner one plan (R-11): counts per class, every ask item, every rewrite, every held move, and 20 sample lines of the record-or-archive call | the standard (SL-1, SL-2) as the helpers' rules; the gap list with rule-decided classes, so hidden sets, secrets and the kit never reach a helper (SL-7, SL-6); findings by line (SL-5 to SL-12); the counts, asks, rewrites, holds and hash (SL-13) |
| 3: move on the yes | the product's CTO, by hand | Moves what the approved plan moves (code and tests stay, R-05), rewrites the listed references, writes the path map from the standard, rebuilds memory, runs the selected tests, runs the check again with `--moved`; anything red rolls back | the namespaces, policies and stale classes (SL-2, SL-12); the rewrite and held lists (SL-11); the after-move check (SL-14) |
| 4: measure again | EXAMIN's and ASMO OS's CTOs | EXAMIN measures only after its restructure and rebuild, `gov memaudit forbidden-reach` first (C-05); ASMO OS's A6 is this restructure (C-03 (c)) | a clean `--moved` run at the commit the measure uses (SL-14) |

Slice 1 ships to both products by the next release, or by hand if that is sooner: their CTOs run the check from the Gov
OS source tree with `--root` naming their repository.

## Slice 5: drafted, to be finalised when slice 1 lands

These are drafts, not this ticket's KPIs yet. They take their final ids and lines when slice 1 has landed and the two
products' restructures have shown what the code must do.

- Draft SL-15: the path map is generated from the standard and the approved plan (one namespace per class, three for the
  archive, two for study imports, one per import), and a hand edit is named as drift with the way to regenerate (M1, R-04).
- Draft SL-16: code writes the lines a rule decides, splits the rest into up to ten disjoint chunks within the machine's
  gate with hidden sets and secrets removed first, and merges the answers, sending a failing line back at most twice (R-08,
  R-09, rubric §4).
- Draft SL-17: the approved plan is executed by code in batches with rollback points: moves, document rewrites, held items
  left, the map regenerated, memory rebuilt and checked at the commit, the selected tests run, and any red rolled back (M6,
  L4).
- Draft SL-18: archived records resolve by id, marked stale, never current and never superseding; Markdown under imports is
  never a record (M3, C-02); secret-class paths stay out of every index even with the scan off (M5).
- Draft SL-19: a new repository starts in the standard with its generated map (I-25); an import, a tool's install, a trial
  of a tool and a retirement use the same flow and place their material as rubric §5 states (R-12).
- Draft SL-20: on a repository that follows the standard the word check of D3 is retired, its words kept only as a sign; it
  stays on repositories not yet on the standard and is deleted once all but Gov OS follow it (C-01, rubric §8).
- Draft SL-21: EXAMIN and ASMO OS are the proving cases: the generator and the check find both clean without changing a
  file (DEC-1256 (5)).

## Verify

How each K-line is checked; each verify names what the step must produce.

- K1: the committed `template/governance/kernel/standard.yaml` is read and its `classes` entries compared, id by id, with rubric §1's table (destination, `moves`, memory policy, tier, signs); the product is the list of eighteen ids equal to it, `ask` outside it.
- K2: the same file's layout entries compared with rubric §2's tree, L1 to L6, §1's secret and generated patterns, M2's stale classes and the study ceiling; the product is, for a planted path of each class, the destination derived from the file alone.
- K3: `check-jsonschema` with `standard.schema.json` accepts the committed file and refuses each faulty copy, its output naming the faulty key; the file holds a `version`.
- K4: in a planted adopted project, `gov update` to a release holding the file leaves `governance/kernel/standard.yaml` listed in `framework.lock`; an edit makes `gov doctor` report lock drift; with the project's copy removed from a repository, `gov layout check` from the source tree and from the installed package copy still runs; with every shipped copy absent it refuses naming the file.
- K5: `gov layout check <plan> --root <planted repo> --json` on the clean plan gives exit 0 and an envelope with no findings; each faulty plan gives exit 1 and a finding holding code, line and path; an unreadable plan, a broken standard, a non-repository and a modified tracked file each give exit 2 with `LAYOUT_CANNOT_RUN`; `git status --porcelain` and HEAD are unchanged after every run.
- K6: the planted hidden-set and secret-named files are made unreadable and the run gives the same result; the printed text and the envelope hold the paths and the filter's rule id and none of the planted sentinels.
- K7: plans with one line removed, one line doubled, a file line under a folder line, an extra line naming nothing, and a kit file classed as docs give `LAYOUT_GAP`, `LAYOUT_DOUBLE`, `LAYOUT_DOUBLE`, `LAYOUT_NO_ITEM` and `LAYOUT_RULE_CLASS`; an empty plan lists every item once, each rule-decided one with its class.
- K8: one planted line per fault listed gives `LAYOUT_INVALID` naming the field; ten identical reasons pass and an eleventh gives the finding.
- K9: planted wrong destinations for each class, a moved tool-fixed file, a moved test and a moved file under the manifest's package root give `LAYOUT_DESTINATION` with the expected path; the clean plan's destinations of every class give none.
- K10: planted mixed import classes and a split import give `LAYOUT_IMPORT`; a shared and an existing destination give `LAYOUT_TARGET_TAKEN`; the planted hidden-set path, a tracked secret by name, by class and by content give `LAYOUT_STOPPER` with exit 1; the ignored secret file gives none.
- K11: the envelope's `rewrites`, `held` and `kept` lists equal the planted references: a Markdown link, a front-matter path and a moving document's relative link under `rewrites`; the code and configuration mentions holding their item under `held`; a path-map and a tool-written record mention under `kept`; exit 0 on the otherwise clean plan.
- K12: planted overlapping destinations give `LAYOUT_MAP`; the envelope names each namespace with its policies and each study import's chunk count and namespace, the one over the ceiling under keyword search.
- K13: the clean plan run twice and with its lines shuffled gives identical bytes and `hash`; changing one reason, the standard's version or the commit changes `hash`; counts, asks, rewrites, holds and stoppers equal the planted ones.
- K14: `gov layout check <plan> --moved` on the correctly moved copy gives exit 0; each planted after-move fault gives `LAYOUT_MOVE` or `LAYOUT_MAP` naming the path.

## Sources read

- DEC-1255, DEC-1256, DEC-1254 E-02 (`docs/DECISION_REGISTER.md`); `docs/emergency-2/integration/ANSWERS-B-2026-11-26-rubric.txt`.
- `docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md` and the cards of `docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html`.
- `docs/emergency-2/GOLDEN-WORKFLOW.md` (W1, W7, Q-2 to Q-5); `docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md` (the nine-part example and the register).
- `docs/RUBRICS.md`; `.tickets/DAEO-stdl.md`.
- Memory: the brief's bundle (store 691bb72d6f41) and four `gov retrieve` calls on `/home/usain/gov-os-worktrees/W2-00-store`.
