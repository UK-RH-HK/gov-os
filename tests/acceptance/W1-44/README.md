# W1-44 acceptance tests: Phase-2 lessons as lesson records

Written before the implementation by the independent test designer (MR-3) from the ticket's KPI lines,
its `covers` ids and its sources. 5 cases in one file, profile LITE. Every case reads the lesson files
in `docs/lessons/`; one case (S2) builds a temporary project from scratch and calls
`gov.retrieval.retrieve.retrieve`.

Run: `python3 -m pytest tests/acceptance/W1-44 -q -p no:cacheprovider`

## KPI lines and covers ids

| KPI line | covers | test |
|---|---|---|
| S1 scoped, schema-valid lesson records (L-0074, anti-stall, no-manufactured-history, anti-snowball, Phase-2 root causes) | CAP-41.d | `test_lessons_exist_and_are_schema_valid` |
| S2 `gov retrieve` returns each lesson for a ticket in its scope | — | `test_retrieve_returns_lessons_for_ticket_in_scope` |
| S3 the anti-snowball lesson states the one-disposition rule | CAP-59.c | `test_anti_snowball_lesson_states_one_disposition_rule` |
| F1 no lesson lacks scope, severity or source reference | — | `test_every_lesson_has_scope_severity_and_source` |
| F2 no lesson restates policy as authority | CAP-41.b | `test_no_lesson_restates_policy_as_authority` |

## Expected red before the implementation

All 5 cases fail at the `lessons` fixture because `docs/lessons/` is empty:

| reason | cases |
|---|---|
| `no lesson records exist in docs/lessons/` | all 5 |

No case fails on a behaviour assertion before the lesson files exist; none passes.

## What each case needs

* `test_retrieve_returns_lessons_for_ticket_in_scope` needs `gitleaks` on PATH and `sqlite_vec` importable
  (`needs` marker; the case skips with the reason when one is absent). All other cases need only `pyyaml`
  and `jsonschema`, both installed.
* The retrieve case uses `OllamaStandIn` and the stand-in reranker from `w1_21_support`: no model runs, no
  Ollama, no network beyond a loopback port.
