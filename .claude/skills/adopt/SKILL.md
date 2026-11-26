---
name: adopt
description: >-
  Method for progressive adoption of the Gov OS into a repository through the
  A0-A11 transaction
---
# Adopt

A method for progressive adoption. The guard and the role file decide what each session may do; this skill is the method only (CAP-24.b).

## Progressive adoption

A repository is governable from day one (DEC-006). Full A0–A11 remains the target for `ADOPTED_HEALTHY`, but adoption proceeds in stages with one evidence record per stage (CAP-44, CAP-54).

## Wave 1 scope (DEC-090)

Wave 1 delivers `gov adopt --lite`, covering stages A0–A4, A6, A8 and A5:

- **A0** — safety baseline: clean tree and backup ref.
- **A1** — cold inventory of the repository.
- **A2** — classification of artefacts.
- **A3** — target path map.
- **A4** — batched migration plan with rollback points.
- **A5** — independent review of the path map before any move, by the Independent Auditor role (DEC-090).
- **A6** — controlled migration; a failed batch rolls back to its recorded point.
- **A8** — legacy memory extraction and retirement.

Each stage writes an evidence record. `gov doctor` reports the current adoption level (CAP-54).

## Stage AS: the spec audit (DEC-1200 (4))

After A2 and before A3, `gov adopt --lite --stage AS` audits the repository's specs against its code, so that the path map and A5's review see which specs are alive. It reads A1's inventory and A2's classes and commits `governance/adoption/AS-spec-audit.md`, which stands on A2's record. A3 refuses to run before that record is committed, or when it no longer stands on A2's record as that record now is, and A3's record names the AS record it read. AS is a side record of the chain: the stages after A3 do not read it, so an adoption recorded before AS existed goes on, and AS can be run there at any time after A2.

- **The record** lists every spec found (path, title, its stated wave or status); each spec built, partly built or not built, with its evidence (code paths, tests, commits); the tickets found, done or not, by wave; the specs with no code; the code with no spec (the top-level code modules no spec names); and each gap as one question to the owner, with a place for the answer.
- **Built or not** is judged from code paths, tests and commits only, never by a model.
- **The lite checks:** the record names every spec and every top-level code module the inventory holds, and every gap carries a question. A3 refuses a record that fails either, and records nothing.
- **AS changes nothing else:** it writes only under `governance/adoption/`, changes no spec and no code, and closes no gap. A gap's answer is the owner's (how and when the spec is established, or the code retired), recorded beside its question when it comes.
- **No auditor session in the lite form:** the path map's reviewer at A5 reads the AS record with the path map.

## Embedding policy (DEC-694, DEC-700)

Every namespace of the target path map states its `embedding_policy`, as one of two values, written exactly so:

- `embedded` — the chunks of the namespace's files reach the semantic vectors.
- `not embedded` — the namespace's files are found by the lexical route only; nothing of them is embedded.

Stage A3 refuses a path map in which a namespace states another value or none, or in which no namespace is `embedded`; it records nothing. Outside adoption an unknown or missing value is read as `not embedded` (DEC-388), and `gov rebuild` and `gov doctor` say "no namespace is embedded" where none is.

## Stale class (W2-212, DEC-1227 D3)

A namespace whose documents are superseded, historical or legacy states `stale_class`, one of `superseded`, `historical` or `legacy`, never guessed from a name. With it the namespace states both policies that keep it out of default memory, or the path map is CONFIG_INVALID naming the namespace:

```yaml
stale_class: legacy
lexical_policy: not indexed
embedding_policy: not embedded
```

`gov retrieve` then leaves those documents out of its default bundle, on every route, even if they were indexed before the class existed; they are found on purpose with `gov retrieve --include-stale` or a question that names the file's path, listed under `stale`, each marked `stale: true` with its `stale_class`.

Stage A3 refuses (`ADOPT_STALE_CLASS`), naming it and recording nothing, a namespace without `stale_class` whose name, or every path, holds the word superseded, historical, legacy or archive (archive is `historical`; whole words). If only some paths or a description field do, A3 records, with a notice under `notices`; move such paths into a classed namespace of their own, never class a catch-all. `gov doctor`'s `stale_class` part reports both, never failing.

## Independent gates (A7 and A10 lite; the rest Wave 3)

Contract v5 has A7 and A10 in Wave 2 in a lite form (CAP-44.f, DEC-741). Each is recorded as its own stage: `gov adopt --lite --stage A7` (or `A10`) `--verdict <path>`, run by the session that ran the stages on the committed record of a fresh Independent Auditor session. That record states `stage`, `verdict` (only `pass` passes), an `auditor_session` that ran no stage, and `checked`: each record checked, with its sha256 at HEAD. It is committed with `Role: independent-auditor`. The gate commits its own record under `governance/adoption/`, with its conditions; a gate that fails commits a failing record.

- **A7** — independent migration verification, by a fresh Independent Auditor session: the A6 migration against the A3 path map and the A4 plan reviewed at A5. The gate also checks that each move of the plan stands in the project.
- **A10** — independent memory verification, by a fresh Independent Auditor session: A8's extraction and retirement, the derived state rebuilt from git (`gov rebuild`, CAP-20), and the canary of each index (CAP-55).
- **The verdict** reads each gate's record as named conditions (CAP-44.h (4), (6), (9)). A missing A7 or A10 record is that gate's condition `not met`, never healthy. No gate and no auditor accepts a condition; only the owner does, by name.

Wave 3 (CAP-44.k): A7 and A10 by separate verifier roles (CAP-47.a), A10 over the A9 knowledge fabric, the full A9 (its lite form, the Wave 0 memory practice, is the section below), A11 (full audit) and the full verdict.

## A9: Wave 0 memory practice

An adopted repository gets its memory built in Wave 0, in the order below (A9 lite). The practice record `docs/research/W2-88-memory-practice.md` holds the methods, the figures and the lessons behind each step.

1. Assess the repository and plan its refactoring for full indexing.
2. Census the stated links (records, front matter, trailers, text) and build the graph from them.
3. Build the store with the standard (Gov OS's memory standard, pinned and written in the A9 record) and its refresh (the store rebuilt after every merge, a failed build leaving the last good store in service). [DEC-1098 (1), DEC-1072 (2)]
4. Have the verdict set and the tuning set written, by independent writers under the rubric, both held outside every worktree. [DEC-1071 (1)-(3), DEC-1074 (4)]
5. Measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points. [DEC-1071 (1)-(3), DEC-1074 (4)]
6. Declare and measure the verdict set once, at Wave 0, as the first verdict. From then on it is the repository's standing set: judged end to end every week on the same questions (monthly once the repository is stable), as Gov OS's memory is judged (the standard's bundle read whole by the reader, which ranks it itself, and search again once), against 95 %, behind the walls, counts only: only counts leave its run. It never chooses or judges a fix: fixes are chosen on the tuning set and on the fresh sets' misses. Each month a fresh set, measured once, checks it for fitting, and a standing set found fitted is replaced. A miss stands as it is: it is never re-run in the same week and never re-scored. [DEC-1179 (1)-(4), DEC-1071 (1), DEC-1074 (1), DEC-1098 (1)]
7. Record every method and figure, in the adopted repository's copy of the practice record. [DEC-1072 (2)]

The weekly audit runs from one cron line that A9's ACT package gives the repository's owner's operator, beside the walls; adoption never installs it. A standing set that falls below 95 % is a miss with counts only, handled as the practice record's section 9 states. [DEC-1179 (4), (5), DEC-1101 (2), DEC-1125 (2)]

## Verify clauses for adopted tickets

A repository adopted by Gov OS brings tickets written before adoption, and the brief of a ticket is refused while a KPI line has no `Verify:` clause. The pass below gives such a ticket its clauses and leaves the ready check as it is. [DEC-1130, DEC-1083]

- The pass runs for a ticket about to launch, not for the whole tracker. [DEC-1130]
- A product-spec session writes the clauses; the tool never writes one. [DEC-1130, DEC-1050]
- Three things check the clauses: the tool, the ticket's test designer and the auditor's sample. [DEC-1130, DEC-1083]
- The owner approves the rule once, not ticket by ticket. [DEC-1130]

The tool is `gov adopt`. Its list option prints, for each open or in-progress ticket that has a KPI line with no verify, the ticket id and the labels of those lines, and the answers file names only the tickets about to launch. Its apply option takes the answers file (YAML, outside the repository: ticket id, then label, then clause) and checks it before it writes anything: every named ticket exists and is not closed, every named label exists, every line still lacking a verify is answered, and each clause is text of its own. It then appends ` Verify: <clause>` to the lines' text, editing the text only (no YAML dump, which would lose comments), and adds the marker `verify_pass: <date> <session>` to the ticket's front matter. [DEC-1130]

## Governing sources

DEC-006, DEC-090, DEC-388, DEC-694, DEC-700, DEC-1050, DEC-1071, DEC-1072, DEC-1074, DEC-1083, DEC-1098, DEC-1101, DEC-1125, DEC-1130, DEC-1179, DEC-1200, CAP-44, CAP-54.
