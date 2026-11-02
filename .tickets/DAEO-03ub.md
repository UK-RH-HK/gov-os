---
id: DAEO-03ub
status: open
deps: []
links: [DAEO-fau3]
created: 2026-11-02T10:58:34Z
type: task
priority: 1
assignee: engineer
external-ref: W2-42a
tags: [wave-2, implementation, guard, full]
wbs_id: W2-42a
title: 'The product''s guard reads what a Bash command writes: ACT-GUARD-FIX-3''s eight parser lines in src/gov/guard, before EXAMIN''s copy (DEC-1028 item 4)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/guard/decide.py
- src/gov/guard/reads.py
- src/gov/guard/bash_writes.py
- tests/unit/guard/test_w2_42a*
- docs/changes/W2-42a-evidence.md
kpis:
  success:
  - 'A heredoc''s body is not read as shell: a body that cat, tee or grep takes as data is no write; its unquoted `$(…)` is judged; a `bash`/`sh` body is judged as commands [DEC-1028 item 4, ACT-GUARD-FIX-3 §7 line 1]'
  - 'A variable the command sets once at its top level, before any use, is expanded; a literal `for` loop''s words are judged one by one; any other binding is unresolvable [ACT-GUARD-FIX-3 §7 line 2]'
  - '`$(…)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands; shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command''s name [ACT-GUARD-FIX-3 §7 line 3]'
  - 'An unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable [ACT-GUARD-FIX-3 §7 line 4]'
  - '`git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes; `git apply`, `git am` and `patch` are writes to unresolvable targets [ACT-GUARD-FIX-3 §7 line 5]'
  - 'The read judge does not take `$((…))` for a command substitution, nor a data heredoc''s body for commands [ACT-GUARD-FIX-3 §7 line 6]'
  - 'A backslash-newline outside single quotes is removed before the command is read [ACT-GUARD-FIX-3 §7 line 7]'
  - 'A data heredoc''s body written to a file that a later word of the command may run is judged as that file''s code; a run the parser cannot read is unresolvable [ACT-GUARD-FIX-3 §7 line 8]'
  - 'Measured in docs/changes/W2-42a-evidence.md: on the 61 logged commands the product''s parser resolves the writes of all but at most 2 (today 22 unresolvable); no planted write into the acceptance folder or outside a reviewer''s record is missed; every unknown form still fails closed [DEC-1028 item 4, DEC-958]'
  failure:
  - 'Any write the parser misses that today''s parser catches (a fail-open).'
  - 'An unknown or unparseable form that passes instead of refusing.'
profile: FULL
sources:
- DEC-1028
- DEC-1027
- DEC-958
- DEC-953
est_loc: 600
acceptance_tests:
  path: tests/acceptance/W2-42a/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-42a The product's guard reads what a Bash command writes

The owner's DEC-1028 item 4 (P1-GUARD-PARSER-W2 (a)): ACT-GUARD-FIX-3 fixed this repository's five-rule hook
(`.claude/hooks/bash_writes.py`, `e662684a`), but the product's guard, which every adopted repository runs, keeps the
old parser (`_extract_bash_write_targets` in `src/gov/guard/decide.py`; `_set_aside` and `_Judge.tool`/`command` in
`src/gov/guard/reads.py`) and refuses the writes of 22 of the 61 logged commands it cannot resolve. EXAMIN's agents
would meet those refusals. This ticket brings the eight parser lines (ACT-GUARD-FIX-3 §7) into the product, before
EXAMIN's copy. The engineer may port the reviewed `bash_writes.py` as its basis (a new `src/gov/guard/bash_writes.py`
module); the test designer works from the KPIs and may take the package's planted cases and the logged corpus as
fixtures (no secrets in them). W2-42 (`DAEO-fau3`) keeps its other rows in Wave 3. W2-09 and W2-10 hold
`src/gov/guard/**`: start beside W2-09 only with the files split, or after it. Once it lands, the five-rule hook can
call the product's parser and `bash_writes.py` slims away (a later ACT).
