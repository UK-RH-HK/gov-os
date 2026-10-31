---
id: DAEO-zpdj
status: open
deps: []
links: []
created: 2026-10-31T01:22:30Z
type: task
priority: 0
assignee: product-spec
external-ref: W2-105
tags: [wave-2, specification, template, installs, standard]
wbs_id: W2-105
title: 'The template''s install block removed: an adopted product''s CTO session reaches the guard''s install rule and is asked, as this repository''s is'
class: specification
state_class: AUTHORITATIVE
role: product-spec
depends_on: []
allowed_paths:
- template/.rulesync/permissions.jsonc
kpis:
  success:
  - 'A project generated from the template (copier, then rulesync generate) holds no deny rule for `npm install*` or `pip install*` in its generated settings [DEC-966 item 1, DEC-172]'
  - 'In that project, an install in the CTO''s session (the orchestrator role on its coordination ticket) reaches the guard''s install rule and is asked; in every other session, leads included, it is refused by the guard, as this repository''s after DEC-957 [DEC-966 item 1, DEC-957]'
  - 'Every other permission and deny rule of the template is unchanged: the generated project''s rules counted and compared before and after, by name, only the two install rules gone [DEC-966 item 1]'
  - 'The template''s own suites (W1-38, W1-39) pass on the change [DEC-966 item 1, DEC-965]'
  failure:
  - 'A generated project still denies an install before the guard is asked.'
  - 'An install in a session other than the CTO''s is asked or allowed.'
  - 'Any other permission or deny rule added, removed or changed.'
  - 'W1-38 or W1-39 red on the change.'
profile: STANDARD
sources:
- DEC-966
- DEC-172
- DEC-957
- DEC-965
est_loc: 10
acceptance_tests:
  path: tests/acceptance/W2-105/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer in its own tests worktree (DEC-959 item 7, DEC-963)
track: A
list_rows: []
---
# W2-105 The template's install block removed

Card: the owner's answer to P-W2-90-1 P1-A, (a) (DEC-966 item 1).

- **Why:** `template/.rulesync/permissions.jsonc` lines 7 and 8 deny `npm install*` and `pip install*`. In a generated product Claude Code refuses these before the guard is asked, so the CTO's session can never ask the owner. This repository removed the same rules by DEC-172. Found by W2-90 (`packages/P-W2-90-1.md`).
- **The only generated output:** the rules reach a product through `rulesync generate` in the generated project; no generated copy of them is kept under `template/` (searched), so the one source file is the ticket's path.
- **Then:** after it merges, W2-90's next round moves its 3 cases (W1-05's two orchestrator-asks cases and W1-46's research `npm install` case), with W2-106's 4 and the 14 ids of DEC-965 item 4.
- **Profile STANDARD:** a two-line configuration change, but it decides who is asked about installs in every adopted product.
