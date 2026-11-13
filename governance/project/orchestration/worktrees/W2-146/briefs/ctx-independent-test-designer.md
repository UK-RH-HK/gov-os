{
  "ticket": "DAEO-f6x3",
  "ticket_text": "---\nid: DAEO-f6x3\nstatus: in_progress\ndeps: []\nlinks: []\ncreated: 2026-11-09T01:04:00Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-146\ntags: [wave-2, implementation, retrieval, memory, standard]\nwbs_id: W2-146\ntitle: 'The id reader reads every id form a repository declares: a question that names a nonexistent id in any declared form stops with UNRESOLVED_IDS, so DEC-1071 (5)''s stop can fire in any adopted repository (DEC-1099 (2))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/retrieval/lexical.py\n- src/gov/retrieve/command.py\n- template/governance/kernel/schemas/path-map.schema.json\n- tests/unit/retrieval/test_w2_146*\n- tests/unit/retrieve/test_w2_146*\n- docs/changes/W2-146-evidence.md\nkpis:\n  success:\n  - 'S1 Declared id forms: the path map may declare id forms (an `id_forms:` list, each entry a name and a regular expression), and the path-map schema accepts the list and refuses an entry with no name, no pattern, or a pattern that does not compile. The built-in shape (lexical.ID_SHAPE) stays and is always read. Verify: schema tests on a planted path map with two forms, one with no pattern and one that does not compile [DEC-1071 (5), DEC-1099 (2)]'\n  - 'S2 The reader reads them: `gov.retrieval.lexical.ids_in`, given the root''s declared forms, returns a token of any declared form as an id, whole, once and in order, beside the built-in shape''s ids. With no form declared its result is byte-identical to today''s on the same text. Verify: unit tests on planted id forms the built-in shape does not read (a form with no hyphen, a lowercase form, a form with an underscore, a form with a dotted suffix, a form with a space between its prefix and number), each read when declared and not read when not; a planted text of today''s ids gives the same list with and without forms [DEC-1071 (5), DEC-1099 (2)]'\n  - 'S3 The stop fires on them: `gov retrieve` on a planted store, asked a question that names an id of a declared form that exists nowhere (no record has it, no line of the index holds it as a whole token), stops with UNRESOLVED_IDS, that id a gap UNRESOLVED, no evidence and no continuation. The same id present as a whole token on one line is retrieved as before. The \"every\" rule stays: one named id that exists means the request is retrieved as before. Verify: end-to-end tests on a planted store for each planted form [DEC-1071 (5), DEC-1099 (2), DEC-900]'\n  - 'S4 Nothing else moves: with no form declared, the lexical route''s ranking of a question, the closure''s gaps and the existing UNRESOLVED_IDS cases are unchanged. A declared form changes only what the id reader reads. Verify: the existing retrieval and retrieve unit and acceptance tests pass unchanged [DEC-1071 (5), DEC-1099 (2)]'\n  failure:\n  - 'A question naming a nonexistent id of a declared form answered with unrelated evidence instead of UNRESOLVED_IDS. Verify: S3''s end-to-end test on the planted store, asked for a declared-form id that exists nowhere: the answer is UNRESOLVED_IDS with no evidence; any evidence returned there is this failure'\n  - 'A question naming an existing id of a declared form stopped with UNRESOLVED_IDS. Verify: S3''s end-to-end test with the same id present as a whole token on one line: the answer is retrieved, and UNRESOLVED_IDS is never printed for it'\n  - 'Any change to ids_in''s result, to ranking or to the stop when no form is declared; a path map with a malformed form accepted. Verify: S4''s unchanged existing tests, and S2''s byte-identical comparison of `ids_in` with and without forms on a planted text, all pass; S1''s planted map with a nameless, a patternless and a non-compiling form is refused by the schema each time'\nprofile: STANDARD\nsources:\n- DEC-1071\n- DEC-1099\n- DEC-1098\n- DEC-1097\n- DEC-900\nest_loc: 120\nacceptance_tests:\n  path: tests/acceptance/W2-146/\n  author: 'independent-test-designer (MR-3), from these KPI lines, before the engineer: planted id forms in a temporary path map and a planted store in a temporary folder; no question, label or id from a hidden or spent set, and never this repository''s store'\ntrack: B\nlist_rows: []\nneeds: []\nwaits_on: []\n---\n# W2-146 The id reader reads every declared id form\n\nThe owner's DEC-1099 (2) answer (6): the nonexistent-id row filed as its own ticket now, before the first adoption.\n\n- **The defect:** the product's id reader (`gov.retrieval.lexical.ids_in`) reads only tokens of its one built-in\n  shape (`ID_SHAPE`: a capital letter, then at least one hyphen and a part, with a digit somewhere). A repository\n  whose ids take another form (no hyphen, lower case, an underscore, a space) names ids that the reader does not read\n  as ids, so `gov retrieve`'s stop (`_nowhere` in `src/gov/retrieve/command.py`) never sees them, and DEC-1071 (5)'s\n  `UNRESOLVED_IDS` cannot fire for a question naming a nonexistent id in such a form. Found at the fresh 80's\n  pre-flight (`governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md`, \"What follows\"); an adopted\n  repository will have more such forms (W2-88-STANDARD-1 \u00a75).\n- **The fix (W2-88-STANDARD-1 \u00a75):** the id forms read from the path map, beside the built-in shape. The forms used\n  by this repository's own records need no declaration; whether this repository's path map declares any form is the\n  CTO's record change, not this ticket's.\n- **Until it lands:** W2-88's S12 and S14 score the nonexistent-id question on the reader's \"not found\", apart from\n  the bar, and record the stop as \"not applicable\" (W2-88-STANDARD-1 \u00a75).\n- **Tests first:** an independent test designer writes `tests/acceptance/W2-146/` from these lines on planted id\n  forms, before the engineer starts. No hidden or spent question's form is named in a test or a record.\n- **Overlaps:** `src/gov/retrieve/command.py` is also written by W2-116 (`DAEO-f58b`) and W2-138 (`DAEO-rmhj`), both\n  in progress; `src/gov/retrieval/**` by W2-32 (`DAEO-0pyc`), closing at the lift. `gov plan` orders them; the second\n  to merge merges back. `gov.links` has its own `ids_in` (`src/gov/links/check.py`), not touched here.\n- **Profile STANDARD:** a narrow change to what the reader reads, with no change when no form is declared (S4). It\n  touches the stop that keeps unrelated evidence from being offered, so a fault fails open: hence tests first and an\n  independent review.\n- **Est.:** about 120 lines with tests, half a day with its review.\n\n[DEC-1099 (2), DEC-1071 (5)]\n\n## Interface (DEC-1052; P-W2-146-1 (a): the lead's proposal accepted as a whole, the CTO, 2026-11-12 09:25)\n\nThe ticket names the reader (`ids_in`), the stop (`_nowhere`) and the key (`id_forms:`), but not the entry's shape,\nthe reader's call form, how a declared match is bounded, how it meets the built-in shape, what a malformed form does\nat run time, or the test seams. Proposed:\n\n1. **Schema** (`template/governance/kernel/schemas/path-map.schema.json`): an optional top-level `id_forms`, an array\n   (may be empty: nothing declared) of `$defs/id_form` = `{\"type\":\"object\",\"additionalProperties\":false,\n   \"required\":[\"name\",\"pattern\"],\"properties\":{\"name\":{\"$ref\":\"#/$defs/text\"},\"pattern\":{\"type\":\"string\",\n   \"minLength\":1,\"format\":\"regex\"}}}`. \"Does not compile\" is judged by\n   `jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())` (its `regex` check is Python's\n   `re.compile`); S1's schema tests validate that way. Nothing else in the schema changes; the top level stays open as\n   today, and `src/gov/config/loader.py` (not in the paths) is untouched: it ignores the key, as it ignores\n   `evaluation_sets`.\n2. **Reading the forms**: new `gov.retrieval.lexical.id_forms(root) -> tuple[re.Pattern, ...]`, reading only\n   `id_forms` of `<root>/governance/project/path-map.yaml` with `read_yaml` (as `kept_out` reads `lexical_policy`).\n   No file, no key, or an empty list: `()`. An entry that is not a map, has no non-empty string `name` or `pattern`,\n   or whose pattern does not compile: `GovError(\"CONFIG_INVALID\", ...)` naming `id_forms[<i>]` and the reason\n   (loud, never ignored: an ignored form is the stop failing open). Patterns compiled with no flags (case-sensitive);\n   inline flags at the pattern's start are the repository's.\n3. **The reader**: `ids_in(text: str, forms: Sequence[re.Pattern] = ()) -> list[str]`. `forms=()` runs today's\n   expression unchanged (byte-identical, S2/S4). With forms: the candidates are the built-in shape's matches that hold\n   a digit (today's filter) and each form's `finditer` matches (`group(0)`), a form's match kept only when non-empty and\n   a whole token by `whole_id`'s rule (no word character or `-` before; after, no word character and no `-` a word\n   character follows), checked at the match's span. Overlaps: by start, the longest first; a candidate overlapping\n   one already kept is dropped (so `SPEC-4.2` under a dotted form is read whole, not `SPEC-4` beside it). Then each\n   text once, in order of position.\n4. **Who passes forms**: only `gov.retrieve.command._nowhere`, which calls `forms = lexical.id_forms(root)` once (root:\n   the store root it is given) and uses `ids_in(..., forms)` for both the question and the `--id`/ticket check\n   (`ids_in(name, forms) != [name]`). `_lead_id`, the ranked boost (`search`, lines 519/567), `ID_SHAPE.sub` and\n   `gov.memaudit.preflight` call `ids_in(text)` as today, so indexing and ranking never move (S4). The rest of\n   `_nowhere` (records check, `lexical.search` + `whole_id` per name, the \"every\" rule) and `_stated_gap` are unchanged.\n5. **The refusal's shape**: unchanged (`_stated_gap`): `stopping_reason: \"UNRESOLVED_IDS\"`, `evidence: []`, a gap\n   `{\"id\": <name>, \"reason\": \"UNRESOLVED\"}` per name, `continuation: null`, exit 0. A malformed form makes\n   `gov retrieve` exit 1 with `CONFIG_INVALID` (the envelope's error), before any search.\n6. **Test seams**: S1: the JSON schema file + `Draft202012Validator`/`FormatChecker` on a planted map (the existing\n   valid map from `tests/acceptance/W2-58` or `W1-27` support plus `id_forms`). S2: `ids_in(text, id_forms(tmp_root))`\n   on a planted `governance/project/path-map.yaml` holding only `id_forms`, and `ids_in(text)` for \"not declared\";\n   five planted forms (no hyphen, lowercase, underscore, dotted suffix, space between prefix and number).\n   S3: `gov retrieve --root <tmp store>` (or `gov.retrieve.command.run`) on a planted store built as\n   `tests/acceptance/W2-13/w2_13_support.py` plants one, with the path map declaring the forms; the stop's evidence\n   is the JSON bundle. Runtime `CONFIG_INVALID`: a unit case on `id_forms`.\n\nThe overlap rule (the longest match wins) is accepted with the lead's reason: returning both would let a fragment such as `SPEC-4` stop the refusal for `SPEC-4.2`. Not (b): a malformed form refuses (CONFIG_INVALID), never skipped. Not (c): S4 holds, declared forms reach only the id reader.\n",
  "authority": [
    {
      "id": "DEC-1071",
      "sha256": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "reason": "declared in sources",
      "tokens": 771
    },
    {
      "id": "DEC-1099",
      "sha256": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "reason": "declared in sources",
      "tokens": 693
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1097",
      "sha256": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "reason": "declared in sources",
      "tokens": 1506
    },
    {
      "id": "DEC-900",
      "sha256": "c55f497c5b5db894d54d01f66eda57492fbcd58ef20d5820c17f3b1d89f9b662",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "c55f497c5b5db894d54d01f66eda57492fbcd58ef20d5820c17f3b1d89f9b662",
      "reason": "declared in sources",
      "tokens": 632
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1071",
      "sha256": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "468aa847b29812505c2966b6bd132211008e7137015b6a1dfab93c91ecde2065",
      "reason": "declared in sources",
      "tokens": 771
    },
    {
      "id": "DEC-1099",
      "sha256": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "reason": "declared in sources",
      "tokens": 693
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1097",
      "sha256": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "reason": "declared in sources",
      "tokens": 1506
    },
    {
      "id": "DEC-900",
      "sha256": "c55f497c5b5db894d54d01f66eda57492fbcd58ef20d5820c17f3b1d89f9b662",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "c55f497c5b5db894d54d01f66eda57492fbcd58ef20d5820c17f3b1d89f9b662",
      "reason": "declared in sources",
      "tokens": 632
    }
  ],
  "supplementary": [],
  "supplementary_query": "The id reader reads every id form a repository declares: a question that names a nonexistent id in any declared form stops with UNRESOLVED_IDS, so DEC-1071 (5)'s stop can fire in any adopted repository (DEC-1099 (2))\nS1 Declared id forms: the path map may declare id forms (an `id_forms:` list, each entry a name and a regular expression), and the path-map schema accepts the list and refuses an entry with no name, no pattern, or a pattern that does not compile. The built-in shape (lexical.ID_SHAPE) stays and is always read. Verify: schema tests on a planted path map with two forms, one with no pattern and one that does not compile [DEC-1071 (5), DEC-1099 (2)]\nS2 The reader reads them: `gov.retrieval.lexical.ids_in`, given the root's declared forms, returns a token of any declared form as an id, whole, once and in order, beside the built-in shape's ids. With no form declared its result is byte-identical to today's on the same text. Verify: unit tests on planted id forms the built-in shape does not read (a form with no hyphen, a lowercase form, a form with an underscore, a form with a dotted suffix, a form with a space between its prefix and number), each read when declared and not read when not; a planted text of today's ids gives the same list with and without forms [DEC-1071 (5), DEC-1099 (2)]\nS3 The stop fires on them: `gov retrieve` on a planted store, asked a question that names an id of a declared form that exists nowhere (no record has it, no line of the index holds it as a whole token), stops with UNRESOLVED_IDS, that id a gap UNRESOLVED, no evidence and no continuation. The same id present as a whole token on one line is retrieved as before. The \"every\" rule stays: one named id that exists means the request is retrieved as before. Verify: end-to-end tests on a planted store for each planted form [DEC-1071 (5), DEC-1099 (2), DEC-900]\nS4 Nothing else moves: with no form declared, the lexical route's ranking of a question, the closure's gaps and the existing UNRESOLVED_IDS cases are unchanged. A declared form changes only what the id reader reads. Verify: the existing retrieval and retrieve unit and acceptance tests pass unchanged [DEC-1071 (5), DEC-1099 (2)]\nA question naming a nonexistent id of a declared form answered with unrelated evidence instead of UNRESOLVED_IDS. Verify: S3's end-to-end test on the planted store, asked for a declared-form id that exists nowhere: the answer is UNRESOLVED_IDS with no evidence; any evidence returned there is this failure\nA question naming an existing id of a declared form stopped with UNRESOLVED_IDS. Verify: S3's end-to-end test with the same id present as a whole token on one line: the answer is retrieved, and UNRESOLVED_IDS is never printed for it\nAny change to ids_in's result, to ranking or to the stop when no form is declared; a path map with a malformed form accepted. Verify: S4's unchanged existing tests, and S2's byte-identical comparison of `ids_in` with and without forms on a planted text, all pass; S1's planted map with a nameless, a patternless and a non-compiling form is refused by the schema each time",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 7206,
  "budget": {
    "limit": 9000,
    "used": 7206
  },
  "hash": "fca02f6160a56078ed49e0b7b04667d9247f319dfeaed615b37f1808b29c449c"
}
