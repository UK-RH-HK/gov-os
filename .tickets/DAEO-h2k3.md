---
id: DAEO-h2k3
status: in_progress
deps: [DAEO-m1u3]
links: []
created: 2026-10-29T15:55:50Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-61h
tags: [wave-2, audit, evaluation, held-out, standard, keystone-4]
wbs_id: W2-61h
title: 'W2-61''s enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session'
class: audit
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: [DAEO-m1u3]
allowed_paths:
- fixtures/evaluation/memory-retrieval/visible/q21.yaml
- fixtures/evaluation/memory-retrieval/visible/q22.yaml
- fixtures/evaluation/memory-retrieval/visible/q23.yaml
- fixtures/evaluation/memory-retrieval/visible/q24.yaml
- src/gov/retrieval/measure.py
- tests/unit/retrieval/test_w2_61h_families*
- governance/project/path-map.yaml
kpis:
  success:
  - 'Twenty-eight new questions about this repository''s governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/) [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4)]'
  - 'Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61''s engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2]'
  - 'The spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1 [DEC-954 Q9a, Q9c, DEC-833, DEC-866]'
  - 'Every gold source exists at the commit the auditor reads and holds the answer, cited by path and heading or line [DEC-828 item 4]'
  - 'The hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-1052 G-3, DEC-1055 (4), ACT-D8]'
  - 'The hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by tests that report counts and pass or fail only, never its contents [DEC-954 Q9b, DEC-1052 G-3, DEC-1055 (4)]'
  - 'S7 Source families (DEC-1078 (4), DEC-1079): the measure counts a gold source and its official copies as one family. The families are declared in the path map (`evaluation_families:`, each a list of member path globs, e.g. the Contract''s `docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml` and the generated `docs/contract/capabilities/*.md` and `master-rules/*.md`; the kernel template and its generated `.claude/` and `.rulesync/` copies; `AGENTS.md` and `CLAUDE.md`). An evidence item in another member of the gold source''s family counts as a hit on that source when its text holds the gold span''s text (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the measure''s per-question line; with no family declared, every score is as today; a run''s kept outputs are re-scored with families without running again [DEC-1078, DEC-1079, DEC-1068 (4)]'
  failure:
  - A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work.
  - A question copied from or paraphrasing lens B's visible 20.
  - A gold source that does not hold its answer.
  - 'A family hit counted on a member whose text does not hold the gold span''s text.'
profile: STANDARD
sources:
- DEC-828
- DEC-820
- DEC-845
- DEC-833
- DEC-873
- DEC-941
- DEC-954
- DEC-957
- DEC-950
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-61h/
  author: independent-test-designer (MR-3); form only (count, fields, sources exist), never printing a question or an answer
track: A
list_rows: []
---
# W2-61h W2-61's held-out half: 20 hidden memory questions with their gold sources

**Re-scoped by DEC-954 Q9a; the size confirmed by DEC-957:** 48 questions with lens B's 20 (24 visible, 24 hidden); K9's "memory proven" is judged on the hidden half, at least 21 of 24 hit@5, against the owner's target of 95 %. Est. 12 to 14 lead-hours (MEMORY-SPEC-MAP B.2).

Companion to W2-61 (DEC-941). W2-61's engineer writes the measure and runs the visible half's baseline. The engineer is a measured role (`measures: roles: [engineer, research]` in the path map's `evaluation_sets.memory-retrieval`), so the hidden half is written here, by an independent auditor whose role is not measured, in a session the orchestrator starts, never a retrieval ticket's lead.

- **Why:** a measure tuned on its own questions overstates itself. The hidden half keeps W2-61's figures honest across the memory chain (DEC-828 item 3, DEC-820 (d)).
- **Form:** the auditor reads W2-61's script's input form once it is merged (`src/gov/retrieval/measure.py` and its README or docstring) and writes in that form. Before then, one YAML file per question with `question`, `gold_answer` and `sources` (path plus heading or line).
- **After it:** the orchestrator, which no set measures, runs W2-61's script on the hidden half and records the scores only (never the questions or answers) beside the visible baseline in `docs/research/W2-61-baseline.md`.
- **No path map change:** the hidden folder and its refusal are already in the path map (`evaluation_sets.memory-retrieval`, W2-58).

**DEC-1069 (owner, 2026-11-04 ~13:00):** the set grows to about 40 per half (DEC-1009 amended); **this ticket's category quotas are amended to fit R5** (each governing domain, the plan, tickets, the Contract, decisions and code, at least 10 % of each half; no subsystem above 25 %; at least 3 on failure and lesson memory, at least 2 on the kernel's skills or roles), as stated in `docs/research/memory-measure-audit/RUBRIC.md`'s R5 for a 40-question half; R11 (no answer that changes with ordinary work unless its gold is computed at the measured head) and R1.3 (test-harness code never governs a code fact, except for a question about the harness) apply. The hidden 16 new questions and the corrections of h03 and h08 are written by the owner's operator as the independent checker (ACT-HLABEL-2, ACT-HNEW-1), outside the guard; nothing about them reaches the CTO's session.

**DEC-1079 placed here (CTO, 2026-11-06):** S7, the source families, is DEC-1078 (4)'s rubric row built into the
measure's code, here because W2-61 (the measure's ticket) is closed and this ticket holds the measure's sets. Tests
first (an independent test designer from S7's text, on a planted repository and planted sets), then an engineer; the
CTO re-scores every kept run (`~/gov-os-eval/runs/`) once it lands, counts only.

**S7's interface (CTO, 2026-11-06, delegated P3, from the designer's choices):** (1) `evaluation_families:` is a
top-level key of the path map: a map of a family's name to the list of its member path globs; (2) kept outputs are
re-scored with `python3 -m gov.retrieval.measure <set> ... --kept <dir>`, where `<dir>` holds the kept ranked outputs
in call order (`00001.json` …, beside `.n` and `.n.lock`), and the output is the measure's own; (3) a family hit is
named in the question's line by the member's path and the word "family", the line keeping its present pattern.

**Role changed to engineer (CTO, 2026-11-06, delegated P3):** W2-61h's remaining work is S7's code; `gov launch`
starts an engineer only on an engineer's ticket, and a test designer launches on an engineer's ticket as before. The
guard so keeps S7's engineer from this ticket's own acceptance tests (DEC-1056).

**Role restored to independent-test-designer (CTO, 2026-11-06, the same day):** S2 requires this ticket's questions to
come from no measured role, and its acceptance case checks the ticket's role front matter; the engineer role broke it.
S7's code was built under this ticket's id while the role read engineer (`ab18f6f5`, launched 09:40); the role is
back, and the case passes again. Any later engineering on the measure goes under a ticket of its own.
