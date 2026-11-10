---
id: DAEO-q7lk
status: in_progress
deps: [DAEO-n0wb, DAEO-arrl]
links: []
created: 2026-11-06T13:56:01Z
type: task
priority: 1
assignee: engineer
external-ref: W2-129
tags: [wave-2, implementation, memory, links, standard]
wbs_id: W2-129
title: 'gov links: one cheap, incremental link-integrity check that finds every unlinked or contradicted record across the repository and its memory, and names the role that fixes it; a notice, never a gate (DEC-1073 (5)(b))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-n0wb, DAEO-arrl]
allowed_paths:
- src/gov/links/**
- tests/unit/links/**
- docs/research/W2-129-links.md
kpis:
  success:
  - 'One read-only command: gov links [--since <rev> | --all] [--json] [--propose-marks | --propose-sources] reads HEAD''s records, the register the path map names, ARCHIVE-SUPERSEDED and DECISIONS-IN-FORCE where the project has them, contract.yaml, the kernel texts and the commits, and writes nothing but its mark (.gov-runtime/links/mark, the head it judged); it runs no model, no network and no GPU, and needs no store (it reads HEAD as the loader does) [DEC-1073 (5)(b), DEC-1052, CAP-27]'
  - 'UNMARKED_CHANGE: a decision that another register entry, or ARCHIVE-SUPERSEDED §A, supersedes or amends (a label or free text), whose own entry names no such changer; the finding names both ids, the form that stated the change, and whether the change is whole (ids alone) or of a part [DEC-1073 (5)(b), DEC-866, DEC-825 item 4]'
  - 'UNKNOWN_ID: an id or path in a typed place that names nothing that exists. The typed places are: the register''s labels; a ticket''s sources, closes, depends_on, links, parent, KPI brackets and acceptance_tests.path (in-progress and closed tickets); the Task: and Implements: trailers of the commits judged; contract.yaml''s providers and sources; a lesson''s constrains and sources; a plan''s decisions; a checkpoint''s or close record''s task; a spec''s or change record''s decision keys; the bracketed ids of kernel role, skill and template lines; the ids in test files. A row id that the project''s list file holds, and Task: decision-record (DEC-861), are not findings [DEC-1073 (5)(b), DEC-927, DEC-861]'
  - 'UNLINKED_ID: an id a ticket rests on but does not link, that is one its KPI brackets name, or one a worker commit''s Implements: names, that is not in its sources:. Worker commits are those whose Role: is engineer, independent-test-designer, product-spec, research or independent-auditor, never the landing commits [DEC-1073 (5)(a), DEC-927]'
  - 'STATUS_CONFLICT: two records disagree on a status: a register entry current while ARCHIVE-SUPERSEDED §B calls it spent, or listed in DECISIONS-IN-FORCE while the register says it is superseded or done; a ticket''s status against its close record''s; a generated MR record''s status against contract.yaml''s [DEC-1073 (2)]'
  - 'NOT_IN_FORCE_AS_RULE: a decision whose status is PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED, named in a rule-bearing place: an open or in-progress ticket''s sources or KPI brackets; a judged commit''s Implements:; a register entry''s Under:; a kernel role, skill or template line; a project brief or prompt line; a path-map comment; CONTRACT_v4.md. A PROPOSED decision is never counted as current [DEC-1073 (2)]'
  - 'ENFORCES_SUPERSEDED: W2-55''s gov.decisions.propagation findings, as that module gives them, carried in the same output [DEC-866, DEC-1073]'
  - 'One source of patterns: the register''s statements are read by the loader''s register_statements (W2-92, the census''s patterns), never a second pattern set; on this repository at the clean-up''s starting head the decisions UNMARKED_CHANGE names agree with docs/research/W2-92-proto-drift.py''s drifting list. If W2-92''s product change is not in, the function moves unchanged into src/gov/decisions/statements.py under this ticket and W2-92 imports it [DEC-1072 (1), DEC-1073 (2)]'
  - 'Every finding carries its code, its ids, its path and line, the role responsible and a one-line fix, and is marked (text) when a free-text pattern found it. The role comes from one fixed table by path: the register, .tickets/, plans, prompts, briefs, the path map, lessons and orchestration lists are the orchestrator''s; template/governance/kernel/** and docs/contract/** are product-spec''s; src/** is the engineer''s; tests/** is the independent test designer''s; docs/audit/** is the independent auditor''s; docs/research/** is research''s; a commit''s finding names its Role: and, once landed, the ticket''s lead (orchestrator); any other path is the orchestrator''s [DEC-1073 (5)(b)]'
  - 'Incremental: it reads the whole record set every run and lists in full only the findings that touch what changed in <rev>..HEAD (a record changed, an entry a changed entry names, a commit in the range); the findings older than the mark are counted by code and role on every run and listed with --all. --since gives the range; otherwise the mark does; with neither it refuses, naming --since [DEC-1073 (5)(b), DEC-1052]'
  - 'Its output: a first line "gov links: N new since <rev>, M standing (...)", then one line per new finding (code, ids, path:line, role, fix); --json gives the same findings in gov''s shared envelope. Its exit code is 0 with no new finding, 1 with new findings, and 2 when it cannot run (an unreadable register, not a git work tree), named [DEC-1073]'
  - '--propose-marks prints a patch that git apply accepts, adding to each UNMARKED_CHANGE entry''s status line **Changed by:** DEC-y (the part, where the statement names one), or SUPERSEDED by DEC-y for a whole supersession by ids alone; --propose-sources prints a patch adding each UNLINKED_ID to its ticket''s sources:; neither writes a file [DEC-1073 (5)(a), DEC-866]'
  - 'Never a gate: no command of the close, the merge queue, the landing, gov launch, gov claim, the readiness check or a hook calls it or refuses on its result; the CTO''s structural pass runs it as its links family, a notice only [DEC-1052, DEC-1073]'
  - 'Any repository: it reads the register''s place and the record places from the project''s path map, and a kind the repository does not have (no register, no contract.yaml, no .tickets/) is reported "not applicable", never an error [DEC-1072 (2), DEC-1073 (5)]'
  - 'Cheap, measured: on this repository''s main tree gov links --all finishes in under 10 s and gov links --since HEAD~1 in under 5 s, the median of five runs measured by the CTO and recorded with the head in docs/research/W2-129-links.md, beside the first --all run''s counts by code and role (the clean-up''s baseline). The estimate from today''s parts is about 3 s [DEC-1052 basis (3)]'
  - 'S16 Ticket changes (DEC-1088 (6), standing): a commit in the range that changes a closed ticket''s file (its status closed before the commit) is CLOSED_TICKET_EDITED; a commit that changes an open or in-progress ticket''s title, kpis, allowed_paths, reads, needs, waits_on, depends_on or acceptance_tests with no decision id in the changed lines nor in the commit''s Implements: or Decided-by: trailers is TICKET_CHANGE_UNMARKED; a change of status, assignee or links alone is not a finding. Each names the ticket, the commit and the field, the role orchestrator. Verify: planted commits of each kind [DEC-1088 (6)] [added, DEC-1088]'
  - 'S17 Planted ids in test fixtures (D-6 part 2; DEC-1109 (2), DEC-1098 (3) row 24): in a Python test file (tests/**/*.py), an id that stands inside a string literal that is not a docstring (a fixture''s planted register, ticket, record or path, e.g. REGISTER = """... ### DEC-<n> ...""", "records/decisions/DEC-<n>.md", f"{ACCEPTANCE}/W1-90/test_fixture.py") is a planted id: it gives no UNKNOWN_ID, and an ENFORCES_SUPERSEDED that W2-55''s propagation gives for a test-file line is carried only when the old id also stands on that line outside such a literal (a comment, a docstring, code). Ids in comments and docstrings, and every test file that is not Python (README.md, *.json, *.yaml, *.txt), are judged as today; a Python test file that does not parse is judged as today. W2-55''s module is unchanged (the carrying is the filter). On this repository''s head the 29 ENFORCES_SUPERSEDED places the sitting counted inside planted registers and records leave the standing count, as do the UNKNOWN_IDs on made-up ids inside literals; the 44 README citations stay [DEC-1109 (2), DEC-1098 (3), DEC-1073 (5)(b)]'
  - 'S18 A settlement is a change (D-6 part 2 item F2; DEC-866 (1); DEC-1109 (2)): UNMARKED_CHANGE also names a decision another entry settles (a **Settles:** label, the loader''s register_statements class settle) whose own entry names no such changer, as it does for supersede and amend; the patch --propose-marks gives the same **Changed by:** mark. Every other code and count is unchanged. With W2-55 S9, gov links is then the one relation check, with nothing the old tags check caught left unreported [DEC-866, DEC-1109 (2)]'
  failure:
  - 'A finding that refuses or stops a commit, a close, a landing, a launch or an adoption.'
  - 'Any file written other than the mark; a record changed by the tool; a model, network or GPU call.'
  - 'A finding without its role, path and fix; a free-text finding not marked (text).'
  - 'A second pattern set for the register''s statements; a PROPOSED decision counted as current or as in force.'
  - 'A finding older than the mark lost: neither listed nor counted.'
  - 'gov links --all over 10 s on this repository.'
  - 'A real citation in a test file''s comment, docstring or non-Python file dropped as planted, or a planted literal id still reported (S17) [DEC-1109 (2)]'
profile: STANDARD
sources:
- DEC-1098
- DEC-1109
- DEC-1073
- DEC-1072
- DEC-1071
- DEC-1052
- DEC-866
- DEC-825
- DEC-927
- DEC-861
- DEC-182
- CAP-27
- DEC-1088
est_loc: 400
acceptance_tests:
  path: tests/acceptance/W2-129/
  author: 'independent-test-designer (MR-3); written before implementation, from this ticket''s KPIs and LINK-INTEGRITY.md §4. A planted repository in a temporary folder: a register with each statement form (Changes:, Changed by:, Supersedes: with ids alone and with a part, free text "amended by", an entry with no mark, a PROPOSED and a REJECTED entry), ARCHIVE-SUPERSEDED with §A and §B, DECISIONS-IN-FORCE, tickets with sources, KPI brackets, an unknown id and a missing acceptance path, commits with Task:, Implements: and Role: (a landing commit among them), a lesson, a plan file, a kernel skill line citing a PROPOSED decision, and a contract.yaml with a provider that does not exist; a second planted repository with no register and no tickets. Never this repository''s store. The timing is the CTO''s measured run, not a test.'
track: B
list_rows: []
---
# W2-129 gov links: link integrity, cheap and incremental (DEC-1073 (5)(b))

Card: from DEC-1073 (5)(b): "one tool, cheap and incremental, used by the CTO now and by the Wave 3 orchestrator. It
finds every unlinked or contradicted record across the whole repository and its memory … Each finding names the role
responsible and is fixed straight away. It must pass DEC-1052's basis: cheap, no new gates or ceremony." The design is
`governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md` §4.

- **Why a new ticket (checked):**
  - W2-55 (`DAEO-arrl`) built two decision checks: `gov.decisions.tags` (`STATUS_RELATION_UNMARKED`) and
    `gov.decisions.propagation` (`ENFORCES_SUPERSEDED`). Nothing runs them, and they read the register only.
  - `core-graph` checks `depends_on` and `supersedes` only.
  - `trailer_gate.py` and `traceability.py` check trailers at a lead's return and at the product's close. That close
    has been unused since 28 Oct.
  - `validate_w2.py` checks Wave 2's CAP ids and cards.
  - None reads `sources:`, KPI brackets, other records' id keys, `contract.yaml`'s providers or statuses across
    records. None names a role.
- **What it reuses:**
  - the loader's `register_statements` (W2-92's prototype, `06479938`, with census parity);
  - W2-55's `propagation` as it stands;
  - the store's id grammar.
- **Where it runs:**
  - on demand;
  - in the CTO's structural pass (R1-21), as the family `links`: the CTO adds the line to its own tool, a notice
    only;
  - in adopted repositories through W2-88's kernel declaration (severity `warning`), after a week of use here
    (DEC-1052 (5)).
- **The basis line (DEC-1052, at adoption):** it passes questions 1 to 3: memory, it fails open without it, and it runs
  only on change.
- **Est.:** 400 LOC, about one lead-day:
  - the six kinds, about 220;
  - the owners table, the range and the mark, about 60;
  - the two patches, about 70;
  - the command and the output, about 50.
- **Overlaps:**
  - W2-92 holds `src/gov/store/loader.py`. This ticket only imports `register_statements`.
  - W2-55 holds `src/gov/decisions/**`. This ticket only imports `propagation` and `register`.
  - D-6 later removes `tags.py`'s narrower relation check.
- **What it does not do:**
  - It changes no record.
  - It adds no edge.
  - It is called by no gate.
  - It reads no unindexed scratch file.

**Filed 2026-11-06 by the CTO** from LINK-INTEGRITY-tickets/W2-129-gov-links.md, approved by DEC-1074 (7); placed by D9-FATES (DEC-1083, DEC-1084).

**Built before re-pin window 4 (DEC-1087 (4)). TESTS-READY:** `tests/acceptance/W2-129/` at `5d5fe8abb1cb` on
`w2/W2-129-tests`: 103 cases, 99 red, 4 guards. The KPI success lines are numbered S1 to S15 in the ticket's order, so
never-a-gate is S13 and the timing S15. The interface the tests assume is in their README.

**The designer's points settled (CTO, 2026-11-06, delegated P3):**
- **(2) Exit codes 0, 1 and 2, and the text output:** the command sets `gov.cli.main`'s child exit code (the
  `CHILD_EXIT_CODE` form other commands use) inside `src/gov/links/**`. `cli/main.py` is not changed.
- **(3) Whole or part:** the one pattern set is `register_statements` (S8). Where its reading of a label disagrees with
  the loader's own SUPERSEDES edge (a `**Supersedes:**` followed by plain text), the tool follows `register_statements`
  and states the disagreement in its research record. The loader is not changed here.
- **(4) S8's parity on this repository:** the CTO's check, with whole supersessions apart (the prototype's drifting
  list holds current decisions only).
- **(5) No path-map key** for ARCHIVE-SUPERSEDED or DECISIONS-IN-FORCE: the tool looks in
  `governance/project/orchestration/`, the repository's place. A key is a row for the next pass.
- **(6) `depends_on`** is not a typed place for UNKNOWN_ID (LINK-INTEGRITY §4.1); the store's graph check covers it.
- **(10) MR-1 to MR-6** PROPOSED against `contract.yaml` ACCEPTED: six STATUS_CONFLICTs expected on the first `--all`
  run. They are findings, not a fault of the tool.

**D-6 part 2 placed here (CTO, 2026-11-09; DEC-1109 (2)):** S17 and its failure line are DECIDED-NOT-DONE row 24's "the check to skip test fixtures" (the W2-130 sitting, DEC-1098 (3)). Built as a follow-up on `w2/W2-129-d6` (engineer) after `w2/W2-129-d6-tests` (its test designer, `tests/acceptance/W2-129/`), one review; the plan is `governance/project/orchestration/packages/LIFT-1/D6-PART2.md` item A. `src/gov/links/**` only.

**D-6 part 2 item F2's round 2 placed here (CTO, 2026-11-10; DEC-1109 (2)):** S18. W2-55 S9 removed `tags.py`'s relation check. Its review found that a `**Settles:**` (a change by DEC-866 (1)) is caught by that check but not by UNMARKED_CHANGE, which counts supersede and amend only. Tests first on `w2/W2-129-f2-tests`, the engineer on `w2/W2-129-f2`; W2-55 S9 (`w2/W2-55-f2`) merges with it.
