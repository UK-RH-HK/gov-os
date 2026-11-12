---
id: DAEO-zmo4
wbs_id: W2-174
title: An adopted repository's tickets get their Verify clauses by a checked pass, so gov brief builds their briefs (a list and an apply tool, the adopt skill's step, a marker)
type: task
class: implementation
role: engineer
profile: STANDARD
status: open
state_class: AUTHORITATIVE
priority: 1
created: 2026-11-11 15:21:33+00:00
depends_on:
- DAEO-o5x1  # W2-152: kpi_rows and ready_check in src/gov/brief/build.py, which the tool imports and never changes
- DAEO-2bdu  # W2-88: holds src/gov/adopt/command.py, stages.py and the adopt skill
- DAEO-kmcr  # W2-23: holds src/gov/adopt/** (this ticket adds one module and two flags)
allowed_paths:
- src/gov/adopt/verify_pass.py
- src/gov/adopt/command.py
- src/gov/adopt/facts.py  # the adoption's facts file (DEC-1148 (2), item 4 (a1))
- tests/unit/adopt/test_w2_174*
reads:
- src/gov/brief/build.py
- src/gov/adopt/**
- template/governance/kernel/templates/ticket.md
- template/governance/kernel/schemas/ticket.schema.json
- tests/acceptance/W2-152/**
needs:
- src/gov/brief/build.py       # kpi_rows and the KPI_NO_VERIFY check finished (W2-152)
- src/gov/adopt/command.py     # W2-88's and W2-23's finished state
- template/governance/kernel/skills/adopt/SKILL.md
waits_on:
- ref: DAEO-o5x1
  reason: the tool reads KPI lines with W2-152's kpi_rows, so the list and the check agree
- ref: DAEO-2bdu
  reason: it holds the adopt command and skill files this ticket adds a flag and a step to
est_loc: 180
kpis:
  success:
  - line: "`gov adopt --verify-list --root <repo>` prints, for each open or in-progress ticket in `<repo>/.tickets/` that has a KPI line with no verify, the ticket id and the labels of those lines (S<n>, F<n>), read with `kpi_rows`; it prints `none` and exits 0 when no ticket lacks one [DEC-1130, DEC-1083]"
    verify: "tests/unit/adopt/test_w2_174_list.py: a fixture repository with three tickets (all lines verified, two lines missing, a closed ticket with a missing line) gives exactly the second ticket's two labels; the all-verified fixture prints `none`"
  - line: "`gov adopt --verify-apply <answers-file> --root <repo>` appends ` Verify: <clause>` to each named KPI line of each named ticket, the form `gov brief` already reads, and adds one front-matter line `verify_pass: <date> <session>`; every other byte of the ticket file is unchanged, comments and key order included [DEC-1130, DEC-1050]"
    verify: "tests/unit/adopt/test_w2_174_apply.py: a fixture ticket with YAML comments and a block of five lines; after apply, a byte diff shows only the appended clauses and the one added line"
  - line: "After an apply, `ready_check` of that ticket returns no `KPI_NO_VERIFY` finding, and `gov brief engineer <ticket>` builds its brief on the fixture repository [DEC-1083, DEC-1130]"
    verify: "tests/unit/adopt/test_w2_174_ready.py: calls `gov.brief.build.ready_check` on the applied fixture and finds none; runs `gov brief engineer` on the fixture and gets exit 0 (the fixture carries its own `governance/project/facts.yaml` with every command filled, as an adopted project's CTO fills it after the defaults; DEC-1148 (2))"
  - line: "The answers file is checked by code before anything is written: every named ticket exists and is not closed, every named label exists on it, every line still lacking a verify is answered, and each clause is text of its own (not empty, not only TBD, TODO, n/a or none) [DEC-1130, DEC-1083]"
    verify: "tests/unit/adopt/test_w2_174_checks.py: one case per refusal (unknown ticket, closed ticket, unknown label, an unanswered line, an empty clause, a `TBD` clause), each refused with a named code and nothing written"
  - line: "`gov adopt` writes `governance/project/facts.yaml` when the repository has none: it validates against `template/governance/kernel/schemas/facts.schema.json`, `ready.new_since` is the adoption's UTC date as a quoted ISO string, and every other key holds a product default (gov commands only, nothing of this repository); a command with no product equivalent (`lead_verify`, and `wait_for` until `gov wait` lands) is written as a named placeholder that `gov brief` refuses by name; an existing facts file is left byte for byte [DEC-1148 (2), DEC-1147, DEC-1088 (3)]"
    verify: "tests/unit/adopt/test_w2_174_facts.py: a fixture repository without a facts file has, after the adoption step, a file that validates against the kernel schema and carries ready.new_since equal to the step's date, and `gov brief` there no longer answers BRIEF_FACTS_MISSING (it names the placeholder commands instead); a fixture with its own facts file keeps it byte-identical"
  failure:
  - line: "The apply never writes anything if one entry is refused (all or nothing), never edits a ticket the answers file does not name, never edits a closed ticket, and never marks a ticket `verify_pass` while one of its lines still has no verify [DEC-1130]"
    verify: "tests/unit/adopt/test_w2_174_checks.py: a file with nine good entries and one bad one leaves the whole tree byte-identical; a ticket with one line unanswered is refused and unmarked"
  - line: "The pass never changes `gov brief`, the ready check or the ticket template and schema: a ticket is READY by the same code whether adopted or written here [DEC-1083, DEC-1121, DEC-1122]"
    verify: "the close's diff against the base names no file under `src/gov/brief/`, `template/governance/kernel/templates/` or `template/governance/kernel/schemas/`; `tests/acceptance/W2-152` still passes unchanged"
  - line: "The tool never reads or writes outside `<repo>/.tickets/` and the answers file it is given, and never calls a model or the network [DEC-1130]"
    verify: "tests/unit/adopt/test_w2_174_scope.py: a fixture repository with a decoy file outside `.tickets/` is byte-identical after list and apply; the module imports no network or model package"
non_goals:
- no change to `gov brief` or its ready check (option (c), reading the acceptance folder, is not built here; it is a recorded option for after EXAMIN's copy)
- 'no tracker importer, and no writing of the clauses by the tool: a product-spec session writes them, the tool checks and applies'
- no change to the ticket template or schema; the marker is one extra front-matter line the schema already allows
- no change to W2-88's refactoring-plan text (the CTO's one-line note, below)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1130, DEC-1083, DEC-1052, DEC-1050, DEC-1088, DEC-1121, DEC-1122, DEC-1112, DAEO-o5x1, DAEO-t8mp, DAEO-2bdu, DAEO-kmcr, DAEO-h4rh]
acceptance_tests: {path: tests/acceptance/W2-174/}
---

# W2-174 An adopted repository's tickets get their Verify clauses by a checked pass

**Problem.** `gov brief` refuses a ticket whose KPI lines have no `Verify:` (`ready_check`, `src/gov/brief/build.py`
line 163, `KPI_NO_VERIFY`). A repository adopted by Gov OS brings tickets written before adoption, so no brief can
be built there, and W2-27 (EXAMIN's copy) would stop at its first ticket. DEC-1130 (2) asks for a ticket that lands
first. The approach, with the options (c) the acceptance folder, (d) the pass, (e) combinations, and the costs, is
`governance/project/orchestration/packages/ADOPT-VERIFY-1/APPROACH.md`.

**Approach (if known).** Option (d): a pass for the tickets about to launch. The ready check stays unchanged, so
DEC-1083 holds for every ticket. A product-spec session writes the clauses; the tool lists what is missing, checks
the answers and applies them by editing the lines' text only (no YAML dump, which would lose comments), then marks
the ticket. (c) was set aside: the acceptance folder is written by the test designer after the first brief, so
there is nothing to read for that role, and a folder-level check is coarser than a line-level one.

**Interface.**
- `src/gov/adopt/verify_pass.py`: `missing(root) -> list[{ticket, labels}]`; `apply(root, answers_path, session, today)
  -> list[str]` (the tickets changed); both import `kpi_rows` from `gov.brief.build`. Errors are `GovError` with codes
  `VERIFY_PASS_UNKNOWN_TICKET`, `VERIFY_PASS_CLOSED`, `VERIFY_PASS_UNKNOWN_LABEL`, `VERIFY_PASS_UNANSWERED`,
  `VERIFY_PASS_EMPTY_CLAUSE`.
- Flags on `gov adopt` (they do not need `--lite`): `--verify-list`, `--verify-apply <answers-file>`, `--root`.
- Answers file (YAML, outside the repository): `{<ticket id>: {S1: "<clause>", F2: "<clause>"}}`.
- The marker line: `verify_pass: 2026-11-12 <session id>`, added before the closing `---`.
- A line given as a plain string gets ` Verify: <clause>` appended; a `{line, verify}` mapping already carries a verify
  (the schema requires it) and is never edited.

**Rabbit holes.**
- Do not rewrite a ticket with a YAML dump; edit the text of the lines.
- Do not decide what a clause means (a weak clause is the designer's and auditor's to catch); check only that it is text of its own.
- Do not touch `gov brief`, the template or the schema; do not add an adoption stage (A0 to A8 stay as W2-88 leaves them).

## Widened by the owner (DEC-1148 (2), item 4 (a1), 2026-11-12)

One KPI line (the last success line) and `src/gov/adopt/facts.py`: the adoption writes the facts file `gov brief` needs (`BRIEF_FACTS_MISSING` otherwise), with product defaults and named placeholders; the project's CTO fills its own commands afterwards (for EXAMIN's copy, W2-27's line). S3's fixture carries its own filled facts file. The failure line "the tool never reads or writes outside `<repo>/.tickets/`" concerns the verify pass, not this facts step.

## Its skill line moved (the owner, DEC-1150 (1), 2026-11-12)

S5 (the adopt skill states the Verify pass) moved word for word to W2-88a (DAEO-pg6i, product-spec), with the three skill paths: one ticket of one role writes the adopt skill once, under one CIT-P (DEC-995).
