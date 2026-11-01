# W2-11 round 1: the skill scenarios run (F6, DEC-992), 2026-11-01

Form: each scenario run by a fresh in-session subagent (Opus 5.5) that read only the skill (or the template) under
test, not its `scenarios.md`, was given the scenario's inputs as fictional facts, and wrote nothing: it returned
the content it would write and the commands it would run. The lead judged each by its pass line. Deviation from
"run on a fresh session": no file was written and no commit made, so "the scenarios' commit is older than the
text's" and "the only file written is the report" are judged from the stated order and file list, and the skill
validator is run by the lead on the returned SKILL.md text.

## qa-review 1.0.0

1. A KPI line with no test: **PASS.** The trace names failure line 1 as untraced; the finding carries its two lines
   and a severity (P2); the only file it would write is the findings report; no suite run, no test written, no code
   changed.
   Observation: the session did not find the twelve return fields in qa-review itself (they are in the
   orchestration skill's `briefs-and-returns.md`); a one-line link would let a session loaded with this skill alone
   return them.
2. A hole that needs a deliberate construction: **PASS.** The finding carries `Ordinary work: no, because …` and
   `Consequence: fails open`; it is classed as a row for the hardening list, "not a round", P3; not escalated; the
   only file it would write is the findings report; it re-ran nothing.
   Observation: with only qa-review loaded, it could not quote the two questions word for word (it defers to the
   audit skill for them). Not a pass-line failure.
3. A fail-open in ordinary work that stays unresolved: **PASS.** `Ordinary work: yes, because …`,
   `Consequence: fails open`; P1 (and an Emergency stop); route: the stream's Senior Engineer, then the
   orchestrator, then the owner, never the owner directly; no further repair round; only the report written; code
   and tests unchanged; nothing re-run.
   Observation: same as 2 (the two questions not quotable with only this skill loaded).

## The skill template (`templates/skill.md`)

1. A new skill from the template (a release-note method): **PASS.** Two commits in order: `scenarios.md` first,
   `SKILL.md` second; front matter name, version, a third-person description, `metadata.version`; the eight
   section headings in the template's order (When / not when, Inputs, Steps, Done when, Output and handover,
   Escalation, Never, Sources); body 89 lines; the skill validator on the returned SKILL.md:
   `{"findings": []}`, exit 0 (lead's run, `scenarios/t1/`).
2. More method than fits (a migration review, about 300 lines of detail): **PASS.** Body 90 lines; ten reference
   files directly in the skill's folder, each linked from a step, none linking on; validator `{"findings": []}`,
   exit 0 (`scenarios/t2/`).
3. An imported skill with no licence stated: **PASS.** Not adopted; no text copied; no scenarios written; a
   record of source, version (none) and licence (none) in the skill-import record; a package returned. With MIT
   and 1.2.0 stated: record and scenarios first, text second, marked adopted only in a third commit after the
   three scenarios pass.
   Observations (all three): the template does not give the skill-import record's form; the twelve fields are
   found only through `briefs-and-returns.md`, which the template names (no gap).
