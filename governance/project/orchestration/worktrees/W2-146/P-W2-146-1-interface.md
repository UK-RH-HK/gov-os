## Interface (DEC-1052; P-W2-146-1: the lead's proposal, to be accepted as a whole or amended)

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
