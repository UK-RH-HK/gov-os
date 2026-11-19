# W2-204 evidence record: the memory measure on any adopted repository (DAEO-ma4q)

Written by the engineer, 2026-11-19. It holds the four things the ticket's last section asks for. Nothing here is a
question, a gold answer or a path under a sets root; no real session, measure or rebuild was run for it.

## 1. The generated Gov OS briefs against the approved ones

**How made.** A scratch clone of this branch at `a4ff336b6` (a temporary folder), an empty temporary sets root, no
`MEMAUDIT_CONFIG`:

```
gov memaudit check --repo . --commit HEAD        -> CONFIG ok half 40 categories 12 domains 5 subsystems 7 control memory-retrieval
gov memaudit brief --kind writer  --sets-root <tmp sets> --audit memory-audit-26111901 --commit HEAD --repo . --since HEAD~20 --out <tmp>/writer
                                                 -> BRIEF writer round 1 64d34fb9c48a   (selection: changed 80, sample 300)
gov memaudit brief --kind checker --sets-root <tmp sets> --audit memory-audit-26111901 --commit HEAD --repo . --out <tmp>/checker
                                                 -> BRIEF checker round 1 869dbebdc59e
diff -u governance/project/indep-briefs/memory-audit/<kind>.md <tmp>/<kind>/brief.md
```

| brief | approved (sha256, lines) | generated (lines) | `diff -u`: hunks, lines removed, lines added |
|---|---|---|---|
| writer | `bc0894230e31`, 189 | 179 | 5 hunks, 86 removed, 85 added |
| checker | `cea517b8da7d`, 154 | 149 | 6 hunks, 65 removed, 75 added |

The approved briefs are not changed (pinned by sha; the ticket's non-goal) and Gov OS's walls launcher still uses them.
The differences, by kind:

**A. Expected by the ticket (F-2).** Writer §8: `by_area` was seven fixed areas (`contract`, `decisions`,
`kernel`, `code`, `tests`, `operations`, `docs`); it is now "the governing domain of the question's first
source, under exactly these keys: `decisions`, `tickets`, `plan`, `contract`, `code`, `none`" (the file's
`domains` and `none`). `gov memaudit deliver` refuses a result keyed otherwise.

**B. Gov OS narrative that now comes from the configuration (same content, another place).**
- The category table (names and counts) and the notes under it: from `categories` (`name`, `count`, `about`).
  The `about` texts of Gov OS's file are the approved brief's own sentences; the generated list is one line a
  category, with its count.
- §5 item 3 and the checker's §5a: the five domains with their patterns and the seven subsystems with their patterns
  are listed from `domains` and `subsystems` (the approved text named the subsystems in prose: "retrieval and the
  context packet, the guard, ..."); the numbers 4 and 10 from `spread`.
- §4's rows "the evaluation's own documents", "records of the standing measure that name questions it missed" and
  "the audit's package and walls" are one row listing the file's `exclude` (the walls' `tree-exclude.txt` and the
  paths the approved brief named by hand: the three `W2-8x/W2-92-memory-measure.md` records, the two D4B survey
  files, `MEMORY-AUDIT-1*`, `indep-walls/**`).
- The checker's notes form: the `domains:` and `categories:` lines name the file's domains and categories.
- The draw's 24 and 16, the keyword mark's 6 and the 36-question floor are computed from `half_size` (24, 6 and 36
  of 40, scaled; unchanged at 40).

**C. Generic wording where the approved text named Gov OS's own machinery or records (a real difference).**
- The front matter (`kind`, `tools`, `model`, `budget_usd`, `timeout_s`, `result_schema`) and the "this text
  is hashed ... the launch script starts you headless in your walled folder" paragraph are gone: the product starts no
  session. The generated text says the CTO starts a fresh session and `gov memaudit deliver` takes the output.
- §2: no `CLAUDE.md`; `PIN` is written in the brief itself; the tool list is described ("tools that read files,
  search file names and text, and write files in `out/`") instead of named.
- §4 has no "What enforces it" column: nothing but the brief stops an adopter's session (no wall, no hook). This is
  the one loss of protection against the approved flow; the transcript scan (S12) is what catches a breach afterwards.
- R1: "the highest current record (Charter, Contract, decision, specification, ticket) ... status ACCEPTED ...
  'Changed by' line" is "the highest current record in the repository's own order of authority ... a record counts
  only while it is in force: not a draft, and not a part that a later record replaces". Gov OS's order of authority is
  not in the file (the Interface's key set has no place for it).
- R4: the list of role names is gone ("name to yourself the role and the task").
- R8, R11, §9: "the evaluation's own documents" is "a path §4 names"; "a ticket's `status`", "a closed ticket, a
  decision entry, the plan's rules" are "a status", "a finished record"; "two decisions conflict" is "two records in
  force conflict".
- §5 item 6: "a decision, ticket or capability number past the register's 'Next free id'" is "an id of one of the
  repository's own id forms, past its highest number or outside its range".
- §5 item 3 and §5a: "at least 2 supersession questions; at least 3 failure-memory questions; at least 2 kernel roles
  or skills" are no longer separate set-level sentences: they hold through the categories' notes (Gov OS's `about`
  texts carry "at least 2 are supersession questions", "at least 2 are about roles or skills", "each cites one").
  The checker's notes line "kernel roles or skills <n>, failure or lesson <n>" is gone; `supersession <n>` and the
  draw counts stay.
- "A question counts for what its asked fact is about" (subsystems) is "a question counts for the domain and the
  subsystem of its first source", which is what the pre-flight and `void` compute; the writer is told to list the
  governing source first.
- No template word is a category, domain or subsystem name of Gov OS ("launch script", "retrieval code", "ticket",
  "guard" are reworded), so that a second repository's brief holds none of them (S9).

**D. Not in the brief by design.** `SEED` is in `seed.txt` only (the brief's sha256 is then the same for both
halves' round 1 at one commit); the selection is `input/selection.json`.

## 2. EXAMIN's `governance/project/memory-audit.yaml`

As the lead would write it from EXAMIN's proposal (its requests of 2026-11-19 01:45 and 01:55, the only things of
EXAMIN's read for this). The `about` texts are a draft for EXAMIN's CTO to word. Checked with this branch's code in a
temporary git repository holding one file per domain: `gov memaudit check --repo <tmp> --commit HEAD` prints
`CONFIG ok half 40 categories 12 domains 5 subsystems 7 control none`, and the file validates against
`template/governance/kernel/schemas/memory-audit.schema.json`.

```yaml
version: 1
repository: EXAMIN
half_size: 40
categories:
  - {name: decision, count: 6, about: "a decision or what replaced it (at least 2 are supersession questions)"}
  - {name: task, count: 4, about: "a task record: what it asked for, what it changed"}
  - {name: spec, count: 4, about: "a specification's rule or requirement"}
  - {name: scenario, count: 3, about: "a scenario: its steps, its expected outcome"}
  - {name: report, count: 3, about: "a report or audit: what an attempt found"}
  - {name: exact-string, count: 4, about: "an exact name, id or message, with its file"}
  - {name: callers, count: 4, about: "callers, callees and definitions"}
  - {name: code-paraphrase, count: 4, about: "a code fact asked in other words"}
  - {name: multi-file, count: 3, about: "an answer that needs two or more files"}
  - {name: failure-memory, count: 3, about: "an incident of the build-discipline skill or a failure record; each cites one"}
  - {name: history, count: 1, about: "why or when something changed"}
  - {name: nonexistent-id, count: 1, about: "an id that exists nowhere"}
domains:
  - {name: decisions, paths: ["docs/decisions/**"]}
  - {name: tasks, paths: ["docs/plans/tasks/**", "docs/plans/**"]}
  - {name: specs, paths: ["docs/specs/**", "openspec/specs/**"]}
  - {name: reports, paths: ["docs/reports/**", "docs/audits/**"]}
  - {name: code, paths: ["product/app/**", "product/tools/**", "tests/product/**"]}
subsystems:
  - {name: capture, record_key: feature, values: [F00]}
  - {name: report-suite, record_key: feature, values: [F01]}
  - {name: search, record_key: feature, values: [F02]}
  - {name: authority, record_key: feature, values: [F03]}
  - {name: experiments, record_key: feature, values: [F04]}
  - {name: portal, record_key: feature, values: [F05]}
  - {name: spine, record_key: feature, values: [F06]}
spread: {domain_min: 4, subsystem_max: 10}
exclude: ["archive/**", "docs/audits/wave0/**", ".gov-runtime/**", "product/data/**"]
control: none
```

Notes for EXAMIN's CTO:
- `tasks` lists `docs/plans/tasks/**` before `docs/plans/**` as proposed; the second already holds the first.
- A question whose first source is under `docs/audits/wave0/**` is refused (`PF-EVALNS`): `exclude` wins over the
  `reports` domain.
- The features are read from the `feature` key of the front matter of the question's first source file at the audit
  commit. A code file has none and counts `none`: with code 15 or so of 40 in `none`, no feature can come near 10.
- `control: none` runs the probe search only. `control: {set: <name>, part: visible, size: <n>, baseline: first,
  spread: 2}` is the other choice once EXAMIN has a control set in its sets root: the first measure's figure is
  recorded and later audits are compared with it.

## 3. The commands EXAMIN's CTO runs after `gov update`, from the briefs to the judged figure

Before: the sets root `$R` is a folder outside the repository that holds `governance/project/path-map.yaml` with an
`evaluation_sets:` block (`declare` adds each half's entry there); the repository at the commit holds
`governance/project/path-map.yaml`, `governance/project/retrieval.yaml` and the committed
`governance/project/memory-audit.yaml`; `gov` is the pinned install (`~/.local/bin/gov` into a `pin-<12 hex>`
folder). **The CTO never opens anything under `$R`**: every command below prints counts and codes only, and the
briefs' folders `$W/...` are outside `$R`.

```
D=<EXAMIN's repository>; C=$(git -C $D rev-parse <the pinned commit>); R=<the sets root>; T=<YYYYMMDD of the day>
W=<a work folder outside $R and outside $D>; RUNS=~/gov-os-runs          # the run folder is $RUNS/fresh/$T/

0. gov memaudit check --repo $D --commit $C
       CONFIG ok half 40 categories 12 domains 5 subsystems 7 control none

1. gov memaudit fresh --sets-root $R --repo $D --commit $C --tag $T --runs-dir $RUNS
       FRESH plan: visible memory-audit-<YYMMDD>01 hidden memory-audit-<YYMMDD>02 at <12 hex>
       SNAPSHOT <12 hex> store built            # the clone $RUNS/fresh/$T/repo and its own store: gov rebuild, long
       WAITING memory-audit-<YYMMDD>01 writer-1 # exit 5; V and H below are the two names of the plan line

2. for A in $V $H:
     gov memaudit brief --kind writer --sets-root $R --audit $A --commit $C --repo $D [--since <the last audit's commit>] --out $W/$A/writer-1
     -> a FRESH SESSION (the writer; not the CTO, one per half) is started in a clean checkout at $C with
        $W/$A/writer-1/brief.md as its whole instruction; it writes $W/$A/writer-1/out/
     gov memaudit deliver --kind writer --sets-root $R --audit $A --repo $D --from $W/$A/writer-1/out
       DELIVER writer round 1 files 40

3. gov memaudit fresh ...(as 1)                 # the first pre-flight of each half, recorded
       STEP <A> preflight-1 ok|refused ; WAITING <A> checker-1

4. for A in $V $H:
     gov memaudit brief --kind checker --round 1 --sets-root $R --audit $A --commit $C --repo $D --out $W/$A/checker-1
     -> a FRESH SESSION (the checker; never the writer's) with that brief.md; it writes out/notes.md
     gov memaudit deliver --kind checker --round 1 --sets-root $R --audit $A --repo $D --from $W/$A/checker-1/out

5. gov memaudit fresh ...(as 1)
     either it goes on (6), or for a half whose first pre-flight refused or whose notes hold a revise or reject:
       WAITING <A> writer-2
     gov memaudit brief --kind writer --round 2 ... --out $W/$A/writer-2      -> the writer's FRESH SESSION, round 2
     gov memaudit deliver --kind writer --round 2 ... --from $W/$A/writer-2/out
     gov memaudit fresh ...                                                   -> WAITING <A> checker-2
     gov memaudit brief --kind checker --round 2 ... --out $W/$A/checker-2    -> a checker's FRESH SESSION
     gov memaudit deliver --kind checker --round 2 ... --from $W/$A/checker-2/out

6. gov memaudit fresh --sets-root $R --repo $D --commit $C --tag $T --runs-dir $RUNS \
       --allow-session <each writer's and checker's session id> [--projects ~/.claude/projects]
       STEP <A> void ok ; STEP <A> preflight-final ok ; STEP <A> measure ok ; STEP <A> judge ok   (each half)
       SCAN <V> clean ; SCAN <H> clean          # the transcript scan, from each half's first brief to now
       FRESH VERDICT hidden right <r> of <n> (<p> %): passes|misses
       FRESH BESIDE visible right <r> of <n>    # exit 0

7. gov memaudit figures --sets-root $R --audit $H      # one JSON line of counts, for the record
```

- **What the CTO's fresh sessions do:** steps 2, 4 and 5's writer and checker, each a new session with only its
  folder (`brief.md`, `seed.txt`, `input/`) and a clean checkout at `$C`. Everything else is a command.
- `fresh` is run again after every delivery; it resumes at the step that waited and never repeats a recorded one.
  `WAITING` is exit 5, `STOPPED <A> <step> [<code>]` exit 2 (to the owner: a half void at `void`, a final
  pre-flight refused, a measure or judge stop), `MEASURE VOID <A>` exit 2 with no verdict line (a transcript in the
  window names the half's path or a question id and its session was not allowed), `FR-NAME` exit 1 (the tag's names
  are taken, or its run folder is of another commit: take the next letter, `${T}b`).
- The scan is part of `fresh`. `gov memaudit scan` alone is not needed.
- `--rebuild-cmd "<words>"` replaces the default `gov rebuild` in the clone (for example a seeded build);
  `--gate-cmd` is the resource gate's check before `measure` and `judge`; `--gov` and `--claude` name the
  executables as `measure` and `judge` take them.
- The visible half's kept questions are copied to `$RUNS/fresh/$T/visible/` after its measure: from then on they
  are open. The hidden half stays in `$R`.

## 4. What W2-188's adopt skill step 6 and the practice record should now say (for the CTO; not edited here)

- **Before step 6's measure, a new sentence:** the repository states its own measure tables in
  `governance/project/memory-audit.yaml` (the schema is `template/governance/kernel/schemas/memory-audit.schema.json`):
  its governing domains by path, its subsystems by path or by a record key, its categories with quotas that sum to the
  half size and include `nonexistent-id`, the paths no question may cite, and its control set (`none`, or a set
  with `baseline: first` at a first measure). `gov memaudit check` must print `CONFIG ok`. Without the file every
  step refuses (`MA-CONFIG-MISSING`); Gov OS's tables are never used for another repository.
- **The steps are `gov memaudit <step>`** (`preflight`, `void`, `declare`, `measure`, `judge`, `figures`,
  `brief`, `deliver`, `check`, `fresh`, `scan`), not `python3 -m gov.memaudit` (which still works).
- **A fresh pair of halves is one command run until it ends:** `gov memaudit fresh --sets-root R --repo D --commit C
  --tag YYYYMMDD`, on a snapshot it clones and builds; the repository's own store is not the one measured.
- **The writer and the checker are the adopter's CTO's own fresh sessions**, each given the folder `gov memaudit
  brief` writes and nothing else; their output enters the sets root only through `gov memaudit deliver`. The walls
  launcher (`indep_launch.py`) and the approved briefs under `governance/project/indep-briefs/` are Gov OS's own
  and are not part of what an adopter runs. "Behind the walls" in step 6 holds for Gov OS; for an adopter it reads
  "by independent fresh sessions, closed by the transcript scan".
- **The CTO never reads the sets root;** the transcript scan at the end of `fresh` (or `gov memaudit scan`) is the
  check, and a finding voids the measure.
- **The practice record** (`docs/research/W2-88-memory-practice.md`) should name the file as the place of a
  repository's domains, categories and control, and say that the control's baseline of a repository without an earlier
  figure is its first measure's own figure (`baseline: first`), not Gov OS's 34.
- **The standing set's declaration** (`standing declare`) checks each question's category against the repository's
  file too.
