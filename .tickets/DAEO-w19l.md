---
id: DAEO-w19l
status: in_progress
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-36
tags: [implementation, standard, emergency-2]
wbs_id: W2-36
title: gov discover
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
allowed_paths:
- src/gov/discover/**
- tests/unit/discover/**
- tests/acceptance/W2-36/**
kpis:
  success:
  - 'Discovery opens from an idea and reads what exists [CAP-32.d, DEC-166, W2-M284]. Verify: in a planted project P (a git repository with `.tickets/`, the vendored `governance/kernel/bin/tk`, `openspec/schemas/feature-readiness/` copied from `template/openspec/`, `governance/project/facts.yaml` and the kernel templates copied from this worktree, no memory store, and four planted files: `docs/report.md` and `openspec/specs/report/spec.md` that mention "CSV" and "export", a ticket whose body mentions "report page", and `docs/unrelated.md` that mentions none of the idea''s words), `gov discover "add CSV export to the report page" --json` exits 0; afterwards exactly one new ticket file is under `.tickets/` and exactly one new folder `openspec/changes/add-csv-export-report-page/` holds `proposal.md`, `readiness.yaml` and `spec.md`, and `git status --porcelain` lists nothing else; the JSON result names the change, the specification id, the discovery ticket and the spec path; `proposal.md`''s front matter has `type: specification`, that id, `status: DRAFT`, `profile: LITE`, `spine: false`, `capability_types: []` and `discovery_ticket` naming the new ticket; `readiness.yaml` holds the 26 rows, every one `MISSING` with `gap_ticket: null`; the ticket has `class: specification`, `role: product-spec`, `discovers` naming the change, no `specification` key, `allowed_paths` `[openspec/changes/add-csv-export-report-page/**]`, `reads`, `needs` and `waits_on` as lists, and a success KPI line whose verify is `gov discover --check add-csv-export-report-page`; `spec.md`''s `## Sources read` lists the three planted files that mention the idea''s words and not `docs/unrelated.md`, and says `Memory: not available` with a reason.'
  - 'The draft is a spec in the spec-writing form, with its open questions as packages. Verify: the `spec.md` of the first verify has the nine `##` headings of `template/governance/kernel/skills/spec-writing/spec-form.md` in order, then `## Verify` and `## Sources read`; `## Problem` holds the idea''s words verbatim; `## Open questions` holds one package per row the LITE profile requires (the ten mandatory rows: intent, actor, scenarios, inputs, data_model, outputs, security, success, failure, acceptance_tests, each named in its question) and one package on the profile and capability types, each in spec-form''s package form (a `- Question:` line, an `- Options:` line with at least two options each carrying `(cost: ...)`, a `- Recommendation:` line); the same discovery run with `--profile STANDARD --type performance-capacity` writes those into `proposal.md` and holds packages for the STANDARD rows that type adds (nfr, performance) and no profile package; `gov discover --check` on the unfilled draft exits 1 and refuses, by name, Users and scenarios, Goals, Non-goals, KPIs, Test data, Out of scope and Accepted by, and neither Problem nor Open questions.'
  - 'A finished spec passes the check, every KPI with its failure line and its verify. Verify: in P, the change''s `spec.md` replaced by a planted spec written to spec-form (K1 and K2, each with a `Fails if:` line, a test-data row, every part filled) with a `## Verify` section holding `- K1: <a command and its result>` and `- K2: ...`: `gov discover --check add-csv-export-report-page` exits 0 and prints `PASS`, and also lists each readiness row the profile requires that is open, with its key and its gap ticket or `UNLINKED`, without failing on them; `python3 template/governance/kernel/skills/spec-writing/check_spec.py` on the same file prints `PASS`.'
  - 'Readiness gaps become linked gap tickets, with their dependencies, once [CAP-30.c, MR-2, DEC-089, W2-M283; W2-34 folded]. Verify: in P, a planted change at LITE whose readiness record has every mandatory row PRESENT with evidence except scenarios (MISSING), inputs (MISSING, with `depends_on: [scenarios]` on its row) and acceptance_tests (PROVISIONAL): `gov discover --generate <change> --json` exits 0 and creates exactly three tickets, one per open row; each names its row (`readiness_row` with the specification id, the row number and key) and carries the class and role of the interface''s table (scenarios: discovery, product-spec; inputs: data, product-spec; acceptance_tests: test-design, independent-test-designer); each row''s `gap_ticket` in `readiness.yaml` now names its ticket and no other field of the file changed; the inputs ticket''s `depends_on` lists the scenarios ticket, and the acceptance_tests ticket''s lists the scenarios and inputs tickets (the order of spec work, DEC-103); `gov readiness --specification <id> --json` lists no open row as `UNLINKED`; a second run exits 0, creates no ticket and leaves every file byte-identical; a row whose `gap_ticket` already names an existing ticket gets none.'
  - 'Research is scheduled with an evidence record, and the judgement goes to a brief, never a model call [CAP-32.d, DEC-102, DEC-166]. Verify: in P, `gov discover "add CSV export to the report page" --profile STANDARD --type performance-capacity`, then `gov discover --generate add-csv-export-report-page`: the tickets for the nfr and performance rows have `class: research` and `role: research`, `allowed_paths` holding `docs/research/add-csv-export-report-page/**`, and a success KPI line whose verify names the evidence record `docs/research/add-csv-export-report-page/<row key>.md` with its four parts (what was tested, how, the results with measured numbers, the verdict); `gov brief research <that ticket>` exits 0, and `gov brief product-spec <the discovery ticket>` exits 0 with a brief holding the idea''s words and the path of `spec.md`; the output of `gov discover` and of `--generate` names the `gov brief` command for each ticket it created; no run reads an API key or opens a network connection (each run passes with `ANTHROPIC_API_KEY` unset and `HTTP_PROXY`/`HTTPS_PROXY` set to a closed local port).'
  - 'A spec that passes becomes a feature ticket a test designer can test, accepted by gov brief. Verify: in P, with the passing spec of the third verify, `gov discover --ticket add-csv-export-report-page --paths ''src/report/**'' --paths ''tests/unit/report/**'' --json` exits 0 and writes exactly one new ticket: `class: implementation`, `role: engineer`, `specification` naming the spec id, `allowed_paths` the two given, one success KPI line per K holding its behaviour (with its K id) and its verify, one failure KPI line per K holding its `Fails if:` text and the same verify, `non_goals` the spec''s Non-goals bullets, `reads`, `needs` and `waits_on` as lists, `profile` the proposal''s, and `acceptance_tests.path` `tests/acceptance/<ticket id>/`; `gov brief independent-test-designer <ticket>` and `gov brief engineer <ticket>` each exit 0, and the brief''s KPI table holds every K''s line and verify, none of them `none`.'
  - 'The same request in plain language works the same way [CAP-32.d, DEC-166]. Verify: in a fresh copy of P, `gov discover how could we add CSV export to the report page?` (unquoted words, a question) exits 0 and makes the same change name `add-csv-export-report-page`, the same three files, one discovery ticket, the same `## Sources read` list and the same open-question packages as the first verify; `## Problem` holds the request''s words verbatim.'
  failure:
  - 'The check refuses an unfinished spec by name and never prints PASS for it. Verify: four planted variants of the passing spec, each run through `gov discover --check <change>`: K2''s line removed from `## Verify` (`REFUSED Verify: K2 has no verify`); a `## Verify` line for a K3 that does not exist (`REFUSED Verify: K3 is not a KPI`); K1''s behaviour naming code (the same `REFUSED KPIs: K1 names code (...)` line `check_spec.py` prints); Goals holding only a slot (`- <what the change makes true>`) and an HTML comment (`REFUSED Goals: missing`): each exits 1, prints its line, and does not print `PASS`.'
  - 'gov discover never overwrites or half-writes. Verify: in P after the first verify, `gov discover "add CSV export to the report page"` again exits non-zero with `DISCOVER_EXISTS` naming the folder and creates no ticket; `gov discover` with no words exits non-zero and writes nothing; `--check`, `--generate` and `--ticket` on a change that does not exist exit non-zero with `DISCOVER_CHANGE_NOT_FOUND` naming it; `--ticket` on a spec that `--check` refuses exits non-zero with `DISCOVER_SPEC_NOT_READY` listing the refused lines and writes no ticket; in each case `git status --porcelain` is as before the run.'
profile: STANDARD
sources:
- CAP-32.d
- CAP-30.c
- MR-2
- DEC-166
- DEC-089
- DEC-102
- DEC-103
est_loc: 450
reads:
- template/governance/kernel/skills/spec-writing/**
- template/governance/kernel/skills/discovery/**
- template/openspec/schemas/feature-readiness/**
- src/gov/readiness/**
- src/gov/brief/**
- src/gov/tasks/**
- src/gov/retrieve/**
needs: []
waits_on: []
non_goals:
- No model call of its own; judgement goes to a product-spec or research session through its gov brief.
- It does not decide the open questions, fill readiness rows or close a specification (gov readiness close does).
- It does not change gov check's gap-ticket check, the openspec bridge or the readiness checker.
acceptance_tests:
  path: tests/acceptance/W2-36/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-32.d
- CAP-30.c
- DEC-166
list_rows:
- W2-M284
- W2-M283
---
# W2-36 gov discover

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** CAP-32.d moved to Wave 3 (DEC-841).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-36), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/discover/**` (new), `tests/unit/discover/**`.
- **KPIs:** `gov discover <question or feature>` opens a discovery ticket, runs the discovery skill (readiness gaps, owner questions), and schedules research and experiment tasks whose evidence records back the answer. The same request in plain language works the same way [CAP-32.d, DEC-166, W2-M284].

**D9-FATES (DEC-1083):** Wave 3 by DEC-1083 (D9-FATES, as P1-PLAN §C); the status is kept. First in line in Wave 3 (the discovery agents, aim 2).

**Moved to Wave 3's list 2026-11-16 by the owner (DEC-1201 (3)):** W2-36 leaves Wave 2's list (status `deferred`, tag `wave-2` removed); it is not closed and not done. It is listed in `docs/plan/WAVE_3_PARKING.md` under "Moved from Wave 2 (DEC-1201)". `gov plan` no longer offers it.

**Emergency 2 (2026-11-18): built** (EMERGENCY-2 §6.1 "W2-36 gov discover: build"; §6.2 A-4 "W2-34 fold into W2-36"; §1.1, the aim's pillar "help with the spec and the KPIs"; audit 7 CAP-30.c, CAP-32.d and its release check 28). The KPI lines above are rewritten for it, approved by the CTO's brief to the ticket lead. W2-34 (DAEO-yadm) is folded in: its generation line (CAP-30.c, MR-2, W2-M283) is the fourth success line here; its other lines are not carried (see DAEO-yadm). What it is for: an owner or an agent gets from an idea to a spec whose KPI lines a test designer can test. It gathers, checks and templates by code; where judgement is needed it hands a `gov brief` to a product-spec or research session, never a model call of its own.

**Interface** (what the tests and the code both assume):

- **Commands** (`src/gov/discover/command.py`, an act command; every form takes `--root` and `--json`):
  - `gov discover <words...> [--profile LITE|STANDARD|FULL] [--type <capability type>]...`: opens discovery. The words are joined by one space (quoted or not). Default profile LITE, no types; STANDARD needs at least one `--type` from the readiness schema's table.
  - `gov discover --check <change>`: the spec check. Exit 0 with `PASS` (and the open required rows listed as `OPEN <key> <gap ticket or UNLINKED>`), 1 with its `REFUSED` lines.
  - `gov discover --generate <change>`: one linked gap ticket per required open readiness row not yet linked.
  - `gov discover --ticket <change> --paths <glob> [--paths <glob>]...`: the feature ticket from a spec that passes `--check`.
  - `<change>` is a folder name under `openspec/changes/`.
- **Change name:** the words lower-cased, split on anything not a letter or digit, without the stop words `a an the to of for in on at by and or we i you it can could should would will how what why when where which who do does is are be please let us me my our with into this that`, the first six joined by `-`.
- **What discovery writes** (in the working tree, never a commit): `openspec/changes/<change>/proposal.md` (front matter `id: SPEC-<change>`, `type: specification`, `status: DRAFT`, `profile`, `spine: false`, `capability_types`, `discovery_ticket`; body `# <the words>`), `readiness.yaml` (the schema template's 26 rows, all `MISSING`), `spec.md` (below), and the discovery ticket, made with the project's vendored `tk create` as `gov.tasks.create` does (else `tk` on `PATH`).
- **The draft `spec.md`:** spec-form's nine `##` parts in order, then `## Verify` and `## Sources read`. Problem holds the words verbatim. Each part a session must write holds an HTML-comment guide and a slot (`- <...>`; under KPIs `- K1: <...>` with `  Fails if: <...>`; under Verify `- K1: <...>`). Open questions holds one package per required row at the profile (the row's schema name in the question; options: answer it in this spec, a gap ticket, N/A with a reason; each with its cost; a recommendation) and, when no `--profile` was given, one on the profile and capability types. Sources read lists, by path with its first matching line, each file under `docs/`, `openspec/specs/`, `openspec/changes/` (other changes) and `.tickets/`, and each root `*.md`, that holds a word of the change name, most words first then by path, at most 20; then `Memory:` with the evidence paths of a `gov retrieve` on the words, or `Memory: not available: <reason>` when it cannot run.
- **The check (`--check`):** the spec-writing check (`check_spec.py`'s rules and lines, read from the kernel skill) with two additions: an HTML comment is not content, and a part whose every remaining line is a placeholder (spec-form's placeholder class, bullet removed) is `REFUSED <part>: missing`; under `## Verify`, `- K<n>: <verify>` per KPI: `REFUSED Verify: K<n> has no verify` for a KPI without one (or with a placeholder), `REFUSED Verify: K<n> is not a KPI` for a line naming no KPI. A verify may name code.
- **Gap tickets (`--generate`):** rows are required by `gov.readiness.checker`'s rule for the proposal's profile and types; open is any state but `PRESENT` and `N/A_WITH_REASON`; a row is linked when its `gap_ticket` names an existing ticket. Class and role by row: inputs, data_model, test_data: `data`, product-spec; nfr, integrations, performance, cost: `research`, research; acceptance_tests: `test-design`, independent-test-designer; every other row: `discovery`, product-spec. Each ticket: `readiness_row: {specification, n, key}`, `allowed_paths` `[openspec/changes/<change>/**]` (research adds `docs/research/<change>/**`), `depends_on` the tickets of the rows its row's `depends_on` names (keys or numbers) and, for acceptance_tests, every other gap ticket of the spec (tests come last, DEC-103), `reads`/`needs`/`waits_on` lists, a KPI line with verify "`gov readiness --specification <id>` no longer lists <key> as open" and, for research, one naming the evidence record `docs/research/<change>/<key>.md` and its four parts (DEC-102). The row's `gap_ticket` is written in place; nothing else in `readiness.yaml` changes.
- **The feature ticket (`--ticket`):** as the sixth success line; KPI lines as `{line, verify}` mappings, the line ending with `[K<n>]`.
- **Errors** (`GovError` codes): `DISCOVER_EXISTS`, `DISCOVER_CHANGE_NOT_FOUND`, `DISCOVER_SPEC_NOT_READY`, `DISCOVER_NO_WORDS` (or argparse's usage exit), `READINESS_INVALID` from the checker for a record it cannot judge.

**Known, not this ticket's:** `gov check`'s gap-ticket check (`src/gov/check/claims.py`) flags every `MISSING` row, required or not, so a LITE spec's 16 unrequired rows read as `GAP_TICKET_MISSING` there; `gov readiness` judges only required rows. Noted for the CTO.
