---
id: W2-146-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-12
branch: w2/W2-146
base: 3556fd7d1825
head: 908a6c2527ed (the code reviewed and verified; later commits add only records and the acceptance README's map)
ticket: DAEO-f6x3 (W2-146)
task: DAEO-f6x3
author: orchestrator (W2-146 ticket lead)
review: PASS, independent-auditor session 48f4f52d-2120-40ad-9241-3a24197b79c2 (docs/probes/DAEO-f6x3/PR-DAEO-f6x3.md)
decisions_carried: [DEC-1071, DEC-1099]
decisions_applied: [DEC-1071, DEC-1099, DEC-1052, DEC-1010]
state_class: EVIDENCE
---

# W2-146: change-impact proposal (CIT-P) on the kernel's path-map schema

This change adds an optional `id_forms` list to the kernel's path-map schema, so a repository can declare the id forms
its records use beside the built-in shape, and `gov retrieve`'s stop (DEC-1071 (5)) can fire on a nonexistent id of
any declared form (DEC-1099 (2)). A kernel template file changes, so it goes to the owner before the merge (CAP-33).
The interface was accepted by the CTO as P-W2-146-1 (a), 2026-11-12 09:25 (the ticket's `## Interface`).

## 1. What triggers the change

| # | Trigger | Source | State before this change |
|---|---|---|---|
| T1 | The id reader (`gov.retrieval.lexical.ids_in`) reads only its built-in shape (`ID_SHAPE`), so a question naming a nonexistent id of another form (no hyphen, lower case, an underscore, a space, a dotted suffix) never reaches the stop, and `UNRESOLVED_IDS` cannot fire for it | DEC-1099 (2), the owner's answer (6); DEC-1071 (5); LIFT-1 FRESH-80-RESULT "What follows" | Open |

## 2. The kernel file: `template/governance/kernel/schemas/path-map.schema.json`

| | sha256 |
|---|---|
| before (`3556fd7d1825`) | `7a1a1cd8cbf6fb073e2e1eb6f816d2ba83e2b647e2dc94efb1dfa96f359a8469` |
| after (`908a6c2527ed`) | `d22efa5ada515c8cd0132b8c4960e7aa4d34d4e3fe345b07f576cedfba0fc7be` |

15 lines added, none removed or changed (`git diff --numstat`: `15 0`). The lines added:

```json
    "id_forms": {
      "description": "Optional. The id forms of the project beside the built-in shape: each a name and a regular expression (Python's), read by the id reader of `gov retrieve` (DEC-1071 (5), DEC-1099 (2)). May be empty.",
      "type": "array",
      "items": { "$ref": "#/$defs/id_form" }
    },
```

(a top-level property, after `close_workers`), and

```json
    "id_form": {
      "description": "One id form: its `name` and its `pattern`, a regular expression that compiles; a match is read as an id when it is a whole token.",
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "pattern"],
      "properties": {
        "name": { "$ref": "#/$defs/text" },
        "pattern": { "type": "string", "minLength": 1, "format": "regex" }
      }
    },
```

(a `$defs` entry, before `evaluation_set`). The top level stays open as before; no required key is added, so every
existing path map stays valid. "Does not compile" is judged under `jsonschema.FormatChecker()` (`format: regex` is
Python's `re.compile`).

## 3. What else changes (product code, not kernel)

| File | Change |
|---|---|
| `src/gov/retrieval/lexical.py` (+53 -3) | New `id_forms(root)`: reads only `id_forms` of `<root>/governance/project/path-map.yaml`; none declared: `()`; a malformed entry: `CONFIG_INVALID` naming `id_forms[<i>]` (never skipped). `ids_in(text, forms=())`: with no forms the old expression unchanged (byte-identical); with forms, each form's whole-token matches beside the built-in shape's, the longest at a start kept, each once, in order |
| `src/gov/retrieve/command.py` (+5 -3) | `_nowhere` reads the forms once and passes them to `ids_in` for the question and the `--id`/ticket check; a `CONFIG_INVALID` propagates (exit 1) before any search. No other caller passes forms, so indexing and ranking do not move |
| Tests | `tests/acceptance/W2-146/` (independent test designer), `tests/unit/retrieval/test_w2_146_id_forms.py`, `tests/unit/retrieve/test_w2_146_stop.py` |

## 4. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** (recommended; the owner's DEC-1099 (2) answer (6) files it before the first adoption) | The schema gains `id_forms` as in §2; the reader and the stop as in §3 | This ticket (about 60 lines of product code, 15 schema lines), its tests, one independent review (done, §6) |
| Defer | Keep the one built-in shape until after the first adoption | An adopted repository whose ids take another form gets unrelated evidence for a nonexistent id instead of `UNRESOLVED_IDS` (the stop fails open); W2-88's S12/S14 keep scoring that question apart from the bar |
| Re-baseline | Widen the built-in shape instead of declaring forms | Changes what every repository's reader reads, with ranking and indexing (S4 broken); cannot cover forms nobody foresaw |

## 5. Impact

| Area | Impact |
|---|---|
| Existing path maps | None: the key is optional; with no form declared `ids_in` and the stop are unchanged (S4; the existing retrieval and retrieve suites pass unchanged) |
| `src/gov/config/loader.py`, `src/gov/config/path_map_schema.py` | Untouched; the loader ignores the key as it ignores `evaluation_sets` |
| This repository's path map | Declares no form; whether it should is the CTO's record change, not this ticket's |
| Other kernel files, the guard, the launcher, `gov.links`' own `ids_in` | None |

## 6. Verification and independent review

- **Lead's verification (outside the sandbox, head `908a6c2527ed`, 2026-11-12).** `rebuild_slot.sh`: ok. `lead_verify.sh`:
  5248 tests, 6 failed, 8 skipped (parallel); serial 2 of 2 passed. The six reds are all
  `tests/unit/accept/test_w2_96_*` signal and timeout cases, outside this ticket's paths; re-run alone, 2 passed and
  4 failed, and the same 4 fail on `w2/integrate`'s head `ee242e55` (shared base reds, not this change's).
- **`gov accept W2-146`** (head `ece94c1d4`, after the acceptance README's map named its tests in backticks, td-2
  `86c9af064`): outcome pass, every KPI line passed: S1 20, S2 115, S3 45, S4 12, F1 19, F2 20, F3 46 (with overlap);
  192 passed, 0 failed, 0 skipped, none unmapped.
- **Independent review (CAP-33.d):** a fresh read-only `independent-auditor` (Opus 5.5, effort high, session
  `48f4f52d-2120-40ad-9241-3a24197b79c2`) probed `908a6c2527ed`: **PASS**, five low rows, none in scope, reachable in
  ordinary work and failing open (`docs/probes/DAEO-f6x3/PR-DAEO-f6x3.md`). Its R1 is for the owner: a misspelled
  top-level key (`id_form:`) declares nothing, without a word, because the JSON schema is not run when `gov retrieve`
  loads the path map and the top level stays open (Interface point 1). This holds for every optional path-map key
  today. A follow-up the owner may choose, not in this change: check `path-map.yaml` against this schema in an
  ordinary check (e.g. `gov check`), which would also catch a null `id_forms` and an entry's extra keys (R2, R3).
- **For the owner before the merge (CAP-33):** approve applying the 15 schema lines in §2 (apply now), or choose defer
  or re-baseline (§4).
