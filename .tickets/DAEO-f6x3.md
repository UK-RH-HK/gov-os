---
id: DAEO-f6x3
status: in_progress
deps: []
links: []
created: 2026-11-09T01:04:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-146
tags: [wave-2, implementation, retrieval, memory, standard]
wbs_id: W2-146
title: 'The id reader reads every id form a repository declares: a question that names a nonexistent id in any declared form stops with UNRESOLVED_IDS, so DEC-1071 (5)''s stop can fire in any adopted repository (DEC-1099 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieval/lexical.py
- src/gov/retrieve/command.py
- template/governance/kernel/schemas/path-map.schema.json
- tests/unit/retrieval/test_w2_146*
- tests/unit/retrieve/test_w2_146*
- docs/changes/W2-146-evidence.md
kpis:
  success:
  - 'S1 Declared id forms: the path map may declare id forms (an `id_forms:` list, each entry a name and a regular expression), and the path-map schema accepts the list and refuses an entry with no name, no pattern, or a pattern that does not compile. The built-in shape (lexical.ID_SHAPE) stays and is always read. Verify: schema tests on a planted path map with two forms, one with no pattern and one that does not compile [DEC-1071 (5), DEC-1099 (2)]'
  - 'S2 The reader reads them: `gov.retrieval.lexical.ids_in`, given the root''s declared forms, returns a token of any declared form as an id, whole, once and in order, beside the built-in shape''s ids. With no form declared its result is byte-identical to today''s on the same text. Verify: unit tests on planted id forms the built-in shape does not read (a form with no hyphen, a lowercase form, a form with an underscore, a form with a dotted suffix, a form with a space between its prefix and number), each read when declared and not read when not; a planted text of today''s ids gives the same list with and without forms [DEC-1071 (5), DEC-1099 (2)]'
  - 'S3 The stop fires on them: `gov retrieve` on a planted store, asked a question that names an id of a declared form that exists nowhere (no record has it, no line of the index holds it as a whole token), stops with UNRESOLVED_IDS, that id a gap UNRESOLVED, no evidence and no continuation. The same id present as a whole token on one line is retrieved as before. The "every" rule stays: one named id that exists means the request is retrieved as before. Verify: end-to-end tests on a planted store for each planted form [DEC-1071 (5), DEC-1099 (2), DEC-900]'
  - 'S4 Nothing else moves: with no form declared, the lexical route''s ranking of a question, the closure''s gaps and the existing UNRESOLVED_IDS cases are unchanged. A declared form changes only what the id reader reads. Verify: the existing retrieval and retrieve unit and acceptance tests pass unchanged [DEC-1071 (5), DEC-1099 (2)]'
  failure:
  - 'A question naming a nonexistent id of a declared form answered with unrelated evidence instead of UNRESOLVED_IDS. Verify: S3''s end-to-end test on the planted store, asked for a declared-form id that exists nowhere: the answer is UNRESOLVED_IDS with no evidence; any evidence returned there is this failure'
  - 'A question naming an existing id of a declared form stopped with UNRESOLVED_IDS. Verify: S3''s end-to-end test with the same id present as a whole token on one line: the answer is retrieved, and UNRESOLVED_IDS is never printed for it'
  - 'Any change to ids_in''s result, to ranking or to the stop when no form is declared; a path map with a malformed form accepted. Verify: S4''s unchanged existing tests, and S2''s byte-identical comparison of `ids_in` with and without forms on a planted text, all pass; S1''s planted map with a nameless, a patternless and a non-compiling form is refused by the schema each time'
profile: STANDARD
sources:
- DEC-1071
- DEC-1099
- DEC-1098
- DEC-1097
- DEC-900
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-146/
  author: 'independent-test-designer (MR-3), from these KPI lines, before the engineer: planted id forms in a temporary path map and a planted store in a temporary folder; no question, label or id from a hidden or spent set, and never this repository''s store'
track: B
list_rows: []
needs: []
waits_on: []
---
# W2-146 The id reader reads every declared id form

The owner's DEC-1099 (2) answer (6): the nonexistent-id row filed as its own ticket now, before the first adoption.

- **The defect:** the product's id reader (`gov.retrieval.lexical.ids_in`) reads only tokens of its one built-in
  shape (`ID_SHAPE`: a capital letter, then at least one hyphen and a part, with a digit somewhere). A repository
  whose ids take another form (no hyphen, lower case, an underscore, a space) names ids that the reader does not read
  as ids, so `gov retrieve`'s stop (`_nowhere` in `src/gov/retrieve/command.py`) never sees them, and DEC-1071 (5)'s
  `UNRESOLVED_IDS` cannot fire for a question naming a nonexistent id in such a form. Found at the fresh 80's
  pre-flight (`governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md`, "What follows"); an adopted
  repository will have more such forms (W2-88-STANDARD-1 §5).
- **The fix (W2-88-STANDARD-1 §5):** the id forms read from the path map, beside the built-in shape. The forms used
  by this repository's own records need no declaration; whether this repository's path map declares any form is the
  CTO's record change, not this ticket's.
- **Until it lands:** W2-88's S12 and S14 score the nonexistent-id question on the reader's "not found", apart from
  the bar, and record the stop as "not applicable" (W2-88-STANDARD-1 §5).
- **Tests first:** an independent test designer writes `tests/acceptance/W2-146/` from these lines on planted id
  forms, before the engineer starts. No hidden or spent question's form is named in a test or a record.
- **Overlaps:** `src/gov/retrieve/command.py` is also written by W2-116 (`DAEO-f58b`) and W2-138 (`DAEO-rmhj`), both
  in progress; `src/gov/retrieval/**` by W2-32 (`DAEO-0pyc`), closing at the lift. `gov plan` orders them; the second
  to merge merges back. `gov.links` has its own `ids_in` (`src/gov/links/check.py`), not touched here.
- **Profile STANDARD:** a narrow change to what the reader reads, with no change when no form is declared (S4). It
  touches the stop that keeps unrelated evidence from being offered, so a fault fails open: hence tests first and an
  independent review.
- **Est.:** about 120 lines with tests, half a day with its review.

[DEC-1099 (2), DEC-1071 (5)]

## Interface (DEC-1052; P-W2-146-1 (a): the lead's proposal accepted as a whole, the CTO, 2026-11-12 09:25)

The ticket names the reader (`ids_in`), the stop (`_nowhere`) and the key (`id_forms:`), but not the entry's shape,
the reader's call form, how a declared match is bounded, how it meets the built-in shape, what a malformed form does
at run time, or the test seams. Proposed:

1. **Schema** (`template/governance/kernel/schemas/path-map.schema.json`): an optional top-level `id_forms`, an array
   (may be empty: nothing declared) of `$defs/id_form` = `{"type":"object","additionalProperties":false,
   "required":["name","pattern"],"properties":{"name":{"$ref":"#/$defs/text"},"pattern":{"type":"string",
   "minLength":1,"format":"regex"}}}`. "Does not compile" is judged by
   `jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())` (its `regex` check is Python's
   `re.compile`); S1's schema tests validate that way. Nothing else in the schema changes; the top level stays open as
   today, and `src/gov/config/loader.py` (not in the paths) is untouched: it ignores the key, as it ignores
   `evaluation_sets`.
2. **Reading the forms**: new `gov.retrieval.lexical.id_forms(root) -> tuple[re.Pattern, ...]`, reading only
   `id_forms` of `<root>/governance/project/path-map.yaml` with `read_yaml` (as `kept_out` reads `lexical_policy`).
   No file, no key, or an empty list: `()`. An entry that is not a map, has no non-empty string `name` or `pattern`,
   or whose pattern does not compile: `GovError("CONFIG_INVALID", ...)` naming `id_forms[<i>]` and the reason
   (loud, never ignored: an ignored form is the stop failing open). Patterns compiled with no flags (case-sensitive);
   inline flags at the pattern's start are the repository's.
3. **The reader**: `ids_in(text: str, forms: Sequence[re.Pattern] = ()) -> list[str]`. `forms=()` runs today's
   expression unchanged (byte-identical, S2/S4). With forms: the candidates are the built-in shape's matches that hold
   a digit (today's filter) and each form's `finditer` matches (`group(0)`), a form's match kept only when non-empty and
   a whole token by `whole_id`'s rule (no word character or `-` before; after, no word character and no `-` a word
   character follows), checked at the match's span. Overlaps: by start, the longest first; a candidate overlapping
   one already kept is dropped (so `SPEC-4.2` under a dotted form is read whole, not `SPEC-4` beside it). Then each
   text once, in order of position.
4. **Who passes forms**: only `gov.retrieve.command._nowhere`, which calls `forms = lexical.id_forms(root)` once (root:
   the store root it is given) and uses `ids_in(..., forms)` for both the question and the `--id`/ticket check
   (`ids_in(name, forms) != [name]`). `_lead_id`, the ranked boost (`search`, lines 519/567), `ID_SHAPE.sub` and
   `gov.memaudit.preflight` call `ids_in(text)` as today, so indexing and ranking never move (S4). The rest of
   `_nowhere` (records check, `lexical.search` + `whole_id` per name, the "every" rule) and `_stated_gap` are unchanged.
5. **The refusal's shape**: unchanged (`_stated_gap`): `stopping_reason: "UNRESOLVED_IDS"`, `evidence: []`, a gap
   `{"id": <name>, "reason": "UNRESOLVED"}` per name, `continuation: null`, exit 0. A malformed form makes
   `gov retrieve` exit 1 with `CONFIG_INVALID` (the envelope's error), before any search.
6. **Test seams**: S1: the JSON schema file + `Draft202012Validator`/`FormatChecker` on a planted map (the existing
   valid map from `tests/acceptance/W2-58` or `W1-27` support plus `id_forms`). S2: `ids_in(text, id_forms(tmp_root))`
   on a planted `governance/project/path-map.yaml` holding only `id_forms`, and `ids_in(text)` for "not declared";
   five planted forms (no hyphen, lowercase, underscore, dotted suffix, space between prefix and number).
   S3: `gov retrieve --root <tmp store>` (or `gov.retrieve.command.run`) on a planted store built as
   `tests/acceptance/W2-13/w2_13_support.py` plants one, with the path map declaring the forms; the stop's evidence
   is the JSON bundle. Runtime `CONFIG_INVALID`: a unit case on `id_forms`.

The overlap rule (the longest match wins) is accepted with the lead's reason: returning both would let a fragment such as `SPEC-4` stop the refusal for `SPEC-4.2`. Not (b): a malformed form refuses (CONFIG_INVALID), never skipped. Not (c): S4 holds, declared forms reach only the id reader.
