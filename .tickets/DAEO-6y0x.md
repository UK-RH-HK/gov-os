---
id: DAEO-6y0x
status: open
deps: [DAEO-l78m, DAEO-m1u3]
links: []
created: 2026-10-30T22:14:08Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-93
tags: [wave-2, audit, evaluation, held-out, standard, proving-ground]
wbs_id: W2-93
title: 'W2-81''s held-out half: hidden questions and planted-problem variants per synthetic repository, by an independent session'
class: audit
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: [DAEO-l78m, DAEO-m1u3]
allowed_paths:
- fixtures/evaluation/adoption-proving-ground/validate_hidden.py
- fixtures/evaluation/adoption-proving-ground/hidden/**
- tests/acceptance/W2-81/w2_81_run.py  # the runner's --sets-root, by the independent test designer only (DEC-1144 (6))
- tests/acceptance/W2-81/test_w2_81_runner.py  # its case, the same designer (DEC-1144 (6))
kpis:
  success:
  - 'At least 10 hidden questions per synthetic repository, each with its gold answer, gold sources and forbidden citations, in the form W2-81''s README states Verify: `validate_hidden.py` on a planted stand-in hidden folder prints, for each repository, a question count of 10 or more and exits 0; a planted folder with 9 for one repository is refused; each planted question holds the fields the README states [DEC-957, DEC-941, DEC-828]'
  - 'At least one hidden planted-problem variant per kind that the visible builders do not produce, so an adoption tuned to the visible generator is caught Verify: `validate_hidden.py` on a planted stand-in set prints, for each kind of planted problem the visible builders do not produce, the number of hidden variants per repository; a planted set missing one kind is refused [DEC-941]'
  - 'Written by a session independent of the sessions it measures; nothing hidden written outside the hidden folder; no question or answer quoted in a commit message, a return, a log or a ticket note Verify: the commits of the hidden half carry the independent session''s role; `git diff --stat` shows hidden files only under the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845, DEC-873]'
  - 'Every gold answer is held by the repository the builder builds, checked on a built copy Verify: `validate_hidden.py` on a built copy of a planted stand-in repository: every gold answer is found in it; a planted answer the built copy does not hold is refused naming its id [DEC-828]'
  - 'The hidden half proves its own data valid with an automatic check (`validate_hidden.py`, beside the data, run before every commit of the hidden half and recorded): every forbidden ("must not cite") file names a file of the repository the builder builds, checked on a built copy; every kind of planted problem the visible generator does not produce has at least one hidden variant per repository; anything it cannot read refuses (fail closed); W2-81''s files are not touched Verify: planted stand-in cases: a must-not-cite file absent from the built copy refuses, a kind with no variant refuses, an unreadable file refuses (non-zero exit); `git diff` shows W2-81''s files untouched; each commit of the hidden half has a recorded run [DEC-1010 item 4]'
  - 'The W2-81 runner (`tests/acceptance/W2-81/w2_81_run.py`) and `validate_hidden.py` each take `--sets-root <root>` and find the hidden half under it, so neither the CTO nor a session names the hidden folder on a command line; the runner''s `--hidden <folder>` stays for a direct call; both written by the independent test designer Verify: a planted stand-in sets root holding a stand-in hidden half: the runner and `validate_hidden.py` given only `--sets-root` find and read it, and a root without one exits non-zero naming the missing folder [DEC-1144 (6), DEC-1143 (4)]'
  failure:
  - 'A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session''s sandbox (the guard''s path map) are refused or find it 0 times'
  - 'A question whose gold answer the built repository does not hold. Verify: `validate_hidden.py` on a planted stand-in question whose gold answer the built copy does not hold exits non-zero and names the question id'
profile: STANDARD
sources:
- DEC-957
- DEC-941
- DEC-828
- DEC-820
- DEC-845
- DEC-873
- DEC-1010
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-93/
  author: independent-test-designer (MR-3); form only (counts, fields, sources exist), never printing a question or an answer
track: B
list_rows: []
---
# W2-93 W2-81's held-out half

Card: the WBS's proposed companion "W2-81's held-out half" (§2), filed as MEMORY-SPEC-MAP gap 6, resolved by the owner in DEC-957. Without it W2-81's and W2-88's question figures stand on the visible half only.

- **Starts** once W2-81's README states the hidden half's form and its builders exist. The auditor reads the builders and the README, never edits them.
- **Before it starts, the orchestrator adds an `evaluation_sets` entry** to the path map: `adoption-proving-ground`, `visible: tests/acceptance/W2-81/questions/**`, `hidden: fixtures/evaluation/adoption-proving-ground/hidden/**`; `measures` by tickets (adoption and retrieval builders, the sessions running the adoption under test, and W2-81); the writer's own ticket is not measured. W2-84's refusal then covers it from every worktree.
- **Started by the orchestrator,** never by an adoption or retrieval ticket's lead.

## Widened by the owner (DEC-1144 (6), P1-F (a), 2026-11-12)

The W2-81 runner's `--sets-root <root>` goes here, not in a new ticket: two paths in `tests/acceptance/W2-81/` for the independent test designer who writes `validate_hidden.py`, and one KPI line (the last success line). W2-81 is closed; nothing else in its folder changes. If W1-01's acceptance-author check or the guard refuses a W2-93 commit there, it comes back to the CTO as a package; no other route.
