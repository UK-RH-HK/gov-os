---
id: DAEO-r4xc
status: closed
deps: []
links: []
created: 2026-11-18T23:03:13Z
type: task
priority: 2
assignee: engineer
external-ref: W2-200
tags: [implementation, full, emergency-2]
wbs_id: W2-200
title: "Retire gov context and its module; the close records decisions from the ticket's own sources (M1, DEC-1214)"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: []
waits_on: []
allowed_paths:
- src/gov/context/**
- src/gov/close/**
- src/gov/cli/main.py
- src/gov/check/**
- src/gov/decisions/command.py
- src/gov/adopt/facts.py
- src/gov/util/tokens.py
- src/gov/telemetry/counter.py
- src/gov/telemetry/sessionlog.py
- src/gov/retrieval/supplementary.py
- template/governance/kernel/checks/context-reproducibility.yaml
- tests/unit/close/**
- tests/unit/check/**
- tests/unit/adopt/**
- tests/unit/context/**
- tests/unit/decisions/**
- tests/unit/telemetry/**
- tests/unit/retrieval/**
- tests/unit/cli/**
- tests/unit/links/**
- tests/unit/orchestration/**
- tests/acceptance/**
- tests/optin-lifted-breadth.txt
- tests/acceptance/serial-only.txt
est_loc: 700
kpis:
  success:
  - 'S1 `gov context`, its library and its check are gone. `gov context <ticket>` and `gov context --in-force` exit 2 with the parser''s "invalid choice" naming `context`; `gov --help` lists no `context` command; `src/gov/context/` does not exist and `import gov.context` raises `ModuleNotFoundError`; the kernel holds no `checks/context-reproducibility.yaml` and `gov check` on a fixture repository names no `context-reproducibility` family (a repository whose own `.governance` still lists the family is out of scope). The four helpers that imported the 4-characters-a-token counter from `gov.context` (`telemetry/counter.py`, `telemetry/sessionlog.py`, `check/skill_validator.py`, `retrieval/supplementary.py`) take it from `gov.util.tokens` and count exactly as before. Verify: the command line on a fixture repository; the filesystem; an import in a subprocess; `gov check --json` family names; the existing counter, session-log, skill-validator and supplementary unit tests green unchanged. [DEC-1214 M1 (c); audit 2 Table 1a C9, C12]'
  - 'S2 `--in-force` lives in `gov decisions`. `gov decisions in-force [--root <repo>] [--json]` gives what `gov context --in-force` gave: the digest of the decisions in force, one line `DEC-n — title` per register entry that is neither superseded nor tagged done, in the register''s order, a changed entry as `DEC-n — title (changed by DEC-m)`, then the left-out count (superseded, done) and the register path; `--json` gives the envelope whose `result` is `{lines, left_out: {count, superseded, done}, register}`; it exits 0, also where the repository has no register (`lines: []`, `register: null`). It reads the register from `HEAD`, never the working tree. `gov decisions basis` is unchanged. Verify: a fixture repository whose register holds one plain, one SUPERSEDED, one done-tagged and one changed entry, committed: the text lines and the JSON result are exactly the planted ones; an uncommitted edit of the register changes neither; a repository with no register gives exit 0 and empty lines. [DEC-1214 M1 (c); audit 2 C5]'
  - 'S3 `gov close` records the decisions that govern the change from the ticket''s own sources, resolved in the register by id. The ids are the `DEC-<n>` ids the ticket names in its `sources`, in its optional `decisions` list, and in its KPI lines (success and failure), each once; ids of other forms (CAP-, W2-, MR-, paths, document names) are not decisions and are left alone. The close record holds `decisions_applied` (the ids that stand, sorted by number), and `inputs` holds the ticket''s own entry plus `{id, hash: "sha256:<hex>"}` for each applied decision, the hash being the sha256 of that decision''s span of the register at `HEAD`. The record has no `packet_hash`. The same ticket at the same commit gives the same `decisions_applied` and the same hashes. Verify: a fixture repository that closes a ticket citing `DEC-10` in `sources`, `DEC-11` in `decisions`, `DEC-12` only inside a KPI line, plus `CAP-1`, `W2-9` and a path in `sources`: the close passes and its record holds `decisions_applied == ["DEC-10","DEC-11","DEC-12"]`, the three hashes equal the sha256 of each entry''s span, no `packet_hash`; a decision named in two places is listed once; closing the same ticket again at the same commit gives the same lists. [DEC-1214 M1 (c); EMERGENCY-2 5.5]'
  - 'S4 No size ceiling anywhere in the close. A ticket whose cited decisions are very long (their spans together over 1,000,000 characters) or whose own text is very long closes with no `budgets.close_context_tokens` setting; no `gov` output holds `CONTEXT_OVER_CEILING`, `CONTEXT_FAILED` or `CONTEXT_SETTING_INVALID`; a facts file with `budgets.close_context_tokens: "abc"` (or any value) is ignored, never read, never refused. Verify: the fixture of S3 with a planted register entry of 1,200,000 characters cited from `sources`: the close passes and records it; the same with the setting planted invalid: the close passes; `grep -rn "CONTEXT_OVER_CEILING\|CONTEXT_FAILED\|CONTEXT_SETTING_INVALID\|close_context_tokens" src` finds nothing. [DEC-1214 M1 "no ceiling anywhere"]'
  - 'S5 A decision that no longer stands is recorded as such and never refuses the close. A cited decision whose register entry is SUPERSEDED (by status, by a successor''s `Supersedes`, or by "SUPERSEDED by"), RETIRED or REJECTED is left out of `decisions_applied` and listed in `decisions_not_standing` as `{id, status}` (sorted by number); a decision tagged done still stands and is applied. Verify: a fixture register with one entry of each state cited from `sources`: the close passes, `decisions_applied` holds the standing and the done-tagged, `decisions_not_standing` holds the other three with their states, none is in both. [DEC-1214 M1 (c); audit 2 Table 1a C8 (the refusals the old packet gave)]'
  - 'S6 A decision the register does not hold (amended by the CTO at the land, 2026-11-19: recorded, never refused). A `DEC-<n>` the ticket names in its `sources`, its `decisions` or a KPI line that neither the register at `HEAD` nor the archived register (the path map''s `decision_register_archive`, W2-203) holds is listed in the record''s `decisions_unresolved` and the close goes on: no refusal, no `DECISION_NOT_FOUND`. A decision only the archived register holds is listed in `decisions_not_standing` as `{id, status: ARCHIVED}` and never applied. A project whose path map names no register cannot resolve any id: every cited id is in `decisions_unresolved`. Verify: a fixture ticket citing DEC-999 (in no register) in `sources` and DEC-998 in a KPI line: the close passes its decision step, both are in `decisions_unresolved`, none in `decisions_applied` or `inputs`; a fixture with an archive holding DEC-150 cited from `sources`: `decisions_not_standing` holds `{id: DEC-150, status: ARCHIVED}`; a fixture without a register: every cited id unresolved [DEC-1214 M1 (c): the close records; EMERGENCY-2 2.1: catch and correct, do not prevent; EMERGENCY-2 11.3]'
  - 'S7 The refusal path carries no packet. A refused close with `--disposition` still writes its repair ticket and class, but the repair ticket holds no `context_hash` and no "given without whole-system context" text, and no refusal of `gov close` has the code `CONTEXT_FAILED`; every other refusal code and the ticket''s disposition fields are as before. Verify: a fixture close refused on a red acceptance test with `--disposition repair`: the repair ticket''s fields are those of before minus `context_hash`; a grep of its text for `context` finds no packet line. [DEC-1214 M1 (c); CAP-59.c as the old packet served it]'
  - 'S8 `gov adopt` writes no context entry in the facts. The facts file `gov adopt --facts` writes holds no `commands.context` and no `commands.context_ceiling`, and no text `gov context` anywhere; its step `context_ceiling` stays, as `"on": false` with a `line` that names no command (the unchanged lead templates still carry `{STEP:context_ceiling}`, and `gov brief` drops an off step''s line). Verify: the file written for a fixture repository, parsed: no `commands.context`, no `commands.context_ceiling`, `steps.context_ceiling.on` is false and its line holds neither `{CMD:` nor `gov context`; `gov brief lead <ticket>` on that fixture leaves no `PLACEHOLDER_LEFT`. [DEC-1214 M1 (c); audit 2 Table 1a C7]'
  - 'S9 Every test that asserted `gov context` is retired or rewritten, and the work is listed. No test file under `tests/` outside `tests/acceptance/W2-200/` imports `gov.context`, runs `gov context`, names `context-reproducibility` as a live family or reads `budgets.close_context_tokens` as a live setting. Each retired file is deleted and listed in `tests/acceptance/W2-200/README.md` ("Retired": path, the KPI line or W-id it served, why); each rewritten case carries a `Rewrite-Reason:` line in its docstring that names DEC-1214 M1 and what it asserts now; the README of each acceptance folder touched maps its KPI lines to the surviving tests. The W2-54 context-reproducibility case, W1-24, W2-04, W2-183, W2-13 and W2-55''s context cases are among them; W2-55''s `--in-force` cases move to `gov decisions in-force`. Verify: a W2-200 test that walks `tests/` and fails on each of the four patterns outside its own folder (and outside a retired-files list kept in its README); `gov accept` of each touched W-id green; `tests/unit/close`, `tests/unit/check`, `tests/unit/adopt` green. [DEC-1214 M1 (c); audit 2 Table 1a C16]'
  failure:
  - 'F1 A close never records a decision it did not resolve as applied. An id neither register holds, an archived one, or one that no longer stands, is never in `decisions_applied` and never has a hash in `inputs`. Verify: the fixtures of S5 and S6 read the record.'
  - 'F2 No consumer of the retired packet is left dangling. `gov --help`, `gov check`, `gov close`, `gov adopt` and `gov brief` on a fixture repository never import `gov.context` and never name `gov context` in any output; the existing `gov close` gates (trailers, containment, tests, store freshness, checkpoint) judge as before. Verify: the S1 fixture runs each command and greps stdout and stderr; the existing `tests/unit/close` cases that do not concern the packet are unchanged and green.'
non_goals:
- 'Role files, templates, skills, the SessionStart hook text, `.claude/` and `.rulesync/` copies, and this repository''s `governance/project/facts.yaml` (the entries `commands.context`, `commands.context_ceiling`, step `context_ceiling`, `budgets.close_context_tokens`): kernel and instruction text changes when the CTO decides (EMERGENCY-2 3.5); the lead names each leftover mention in its return'
- 'The `STORE_STALE` gate (`_check_store`) and the store, rebuild and impact code: they serve the close beyond the packet and keep their tests'
- 'Other retired code (G1/G2''s lead removes it tonight), the memory audit''s path table, EXAMIN''s copy'
- 'A new check family that measures the decisions record (the owner''s "or one that measures what replaces it" is not taken up: S3 to S6 are measured by their own tests)'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1214, EMERGENCY-2 5.5, docs/emergency-2/audits/02-memory-in-use.md, docs/emergency-2/audits/OWNER-DECISIONS-2026-11-18.md, DEC-1165, DEC-454, DEC-470]
acceptance_tests:
  path: tests/acceptance/W2-200/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-200: retire `gov context` and its module; the close records decisions from the ticket's own sources

Created 2026-11-18 by the ticket lead from the CTO's brief (EMERGENCY-2 §4.3 step 1; the CTO approves the KPI lines by the brief). The owner's decision (DEC-1214 M1 (c)): "retire the module too; the close (inside the landing) records decisions from the ticket's sources. Everything that depended on `gov context` is replaced by something tested and proven; no ceiling anywhere."

## Interface

- **Gone:** the `context` command (`Command("context", ...)` in `src/gov/cli/main.py`, `src/gov/context/command.py`), the library `src/gov/context/__init__.py`, the check `src/gov/context/context_check.py` and its kernel file `template/governance/kernel/checks/context-reproducibility.yaml`, the close's `_build_context` and the `CONTEXT_FAILED` finding, `close_budget` and the `budgets.close_context_tokens` reading.
- **Moved:** the 4-characters-a-token helper (`_tokens`, `TOKEN_CHARS`) to `gov.util.tokens` (new module, same behaviour); the register's `in_force` digest stays where it is (`gov.util.register.in_force`, also named `gov.decisions.register`) and gets a command: `gov decisions in-force` (a second action of `src/gov/decisions/command.py`, beside `basis`; module top level stays light).
- **New in the close:** a module `src/gov/close/decisions.py` (name free): `decisions_of(root, ticket, front) -> {applied, not_standing, unresolved, inputs}`. It reads the ticket's `sources`, `decisions` (optional list) and KPI lines, takes the `DEC-<n>` ids (`gov.util.register.ids` reads them as whole words), and resolves each in the register `gov.util.register.read(root)` returns (the register of `HEAD`, parsed from git objects; entry `status`, `span`; `superseded` map; `done` set). No store, no ceiling, no retrieval. A decision "stands" unless its entry's status is SUPERSEDED, RETIRED or REJECTED or its id is a key of `register["superseded"]`; a done-tagged entry stands.
- **The close record** (`record` in `src/gov/close/command.py`): `decisions_applied`, `decisions_not_standing` (list of `{id, status}`), `decisions_unresolved` (ids), `inputs` (the ticket's own entry, then `{id, hash: "sha256:<hex of the span's UTF-8 bytes>"}` per applied decision, in the order of `decisions_applied`); `packet_hash` is gone. No refusal for a decision id (S6 as amended): an id neither register holds is `decisions_unresolved`.
- **The refusal path:** `src/gov/close/tool.py`'s repair-ticket text drops `context_hash` and `context_reason`; `_refuse_for` and `_refuse` lose their `context_*` parameters.
- **adopt:** `src/gov/adopt/facts.py`'s `COMMANDS` drops `context` and `context_ceiling`; its step `context_ceiling` is kept `"on": false` with a line that names no command.

Existing tests of the retired behaviour (about 38 files across `tests/acceptance/W1-24`, `W1-30`, `W2-04`, `W2-13`, `W2-54`, `W2-55`, `W2-183` and the other folders `grep -rln "gov context\|gov\.context\|close_context_tokens\|context-reproducibility" tests` lists) are retired or rewritten by the test designer under S9, each rewrite with a `Rewrite-Reason:` naming DEC-1214 M1.

**Closed at the land, 2026-11-19 05:59 (the CTO; EMERGENCY-2 4.3 step 5):** merged as 661c2873d through the landing branch `e2/m1-land` (the lead's `e2/m1-context` at 41ea46789 merged with the integration branch, then fixed). The first broad check on the landing branch (11 unit folders 1,721 passed; 26 acceptance folders 2,116 passed, 55 skipped, 5 failed) found two things, both from this ticket landing beside W2-203 and W2-202: (1) the close refused `DECISION_NOT_FOUND` for any cited decision the register does not hold, which after W2-203 is most of them, and for W2-194's fixture ticket; fixed in two steps: an archived decision is not standing, `ARCHIVED` (f59534941, failing unit cases first), then S6 and F1 amended by the CTO (6a7918fa7: an id neither register holds is recorded unresolved, never refused), the test designer's revision first (3d1ac9587: 3 red in W2-200 and 1 in W1-30 before the change), then the code; (2) gov doctor flagged this ticket's own path `tests/optin-lifted-breadth.txt` as moved (fixed in doctor, 136080645, recorded in W2-203's ticket). The second check on the landing branch merged with the integration branch (W2-206, W2-204, the doctor fix): W1-30's two receipt cases with `--optin=lifted` 2 passed; the acceptance folders W2-200, W2-194, W2-193, W2-203, W2-202, W2-206, W2-115, W2-115b, W2-204 and the unit folders close, queue, accept, doctor, cli, check, optin: 1,269 passed; `gov accept`: W2-200 57 of 57, W2-203 61 of 61, W2-202 39 of 39, W2-206 45 of 45, W2-204 169 of 169. Kernel text the lead changed, accepted by the CTO (3.5): the audit and checkpoint skills, role-lead and role-cto, the facts file. Owed: the `context` key of the kernel's minimum policy (no check behind it); the leftover mentions of `gov context` the lead listed; a case for the scoped and batch closes' decision lists; L2's A2 can start.
