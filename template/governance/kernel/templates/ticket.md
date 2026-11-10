---
name: ticket
version: 1.0.1
role: any
id: PROJ-0000
type: task
status: open
state_class: AUTHORITATIVE
title: The kernel ticket template
---
# The ticket template

A new ticket is the front matter below, between `---` lines, then a short body. Every field is read by code: the schema, the ready check, the guard and the plan.

```yaml
id: DAEO-xxxx
wbs_id: W2-00
title: <the outcome, in one line, imperative>
type: task
class: implementation              # or research, test-design, discovery, data, integration, skill
role: engineer                     # or product-spec, research, independent-test-designer
profile: STANDARD                  # LITE, STANDARD or FULL; FULL only for memory, the five guard rules, launch/close, the queue, data loss
status: open
state_class: AUTHORITATIVE
depends_on: []                     # tickets that must be closed first
allowed_paths:                     # its writes, strict
- src/gov/<area>/**
- tests/unit/<area>/**
reads:                             # the paths it reads, wide; [] is a declared none
- src/gov/<area>/**
needs: []                          # the paths whose finished state it depends on; [] is a declared none
waits_on:                          # the research, specs or tickets it waits on; [] is a declared none
- ref: DAEO-yyyy
  reason: <one line, what it waits for>
est_loc: 120                       # over 400: split (a warning)
kpis:
  success:
  - line: <one observable outcome, present tense> [DEC-n]
    verify: <a command and its expected result, or a file and what it shows>
  failure:
  - line: <what must never happen>
    verify: <the case that shows it refused>
non_goals:
- <what this ticket deliberately does not do>
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]   # the facts file's dod, by id
sources: [DEC-n, CAP-n]
acceptance_tests: {path: tests/acceptance/W2-00/}
```

The body, after the front matter, holds four short parts under the heading `# W2-nn <title>`:
- **Problem.** Two or three sentences: who is hurt, how, the evidence (a path, a count).
- **Approach (if known).** One paragraph; alternatives in one line each, or "none worth a note".
- **Interface.** Where config lives, error names, function signatures: what the tests and the code both assume.
- **Rabbit holes.** What to avoid, one line each.

## Filling it in
- Write each KPI line as one observable outcome with its `verify`: a command and its expected result, or a file and what it shows [DEC-1050].
- Put in `sources:` every decision and capability the KPI lines' brackets name [DEC-1073].
- Put only tickets in `depends_on:`, and in `closes:` only ids the register, the Contract or the list holds [DEC-1073].
- Set `reads:`, `needs:` and `waits_on:` on every new ticket, an empty list as a declared none; each `waits_on` item is an id or record path, or `ref:` with a one-line `reason:` [DEC-1088].
- State the interface in the ticket before the test designer and the engineer start [DEC-1052].
- Quote the Definition of Done by id (`done_when:`), never by copying its lines [DEC-1052].
- Keep history in the register and the close record, never in the ticket [DEC-1052].
