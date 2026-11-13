# Brief td-1: independent test designer for DAEO-f6x3 (W2-146), profile STANDARD, class C2

You write the acceptance tests for ticket DAEO-f6x3 (W2-146): the id reader reads every id form a repository declares,
so a question naming a nonexistent id of a declared form stops with UNRESOLVED_IDS (DEC-1071 (5), DEC-1099 (2)). An
engineer implements in parallel in another worktree; you never read or wait for their work. Write the tests from the
KPI lines and the ticket's `## Interface` only (the test-design method: `.claude/skills/test-design/` or
`template/governance/kernel/skills/test-design/`). Read the existing code only for its public call forms and for test
support to reuse; never design to the implementation. The tests must be red on your branch's head now (nothing is
built yet) for the reason the KPI names, and green once the Interface is built as written.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-146-tests |
| branch | w2/W2-146-tests |
| your paths | tests/acceptance/W2-146/ only (test files `test_w2_146_*.py`, a `w2_146_support.py` if you need one, a `conftest.py` if you need one, a `README.md` mapping each KPI line to its tests) |
| ticket (read it first: S1-S4, F1-F3, and the `## Interface` at its end, which is binding) | /home/usain/gov-os-worktrees/W2-146-tests/.tickets/DAEO-f6x3.md |
| the schema (S1) | template/governance/kernel/schemas/path-map.schema.json (read; a valid planted map: tests/acceptance/W2-58/w2_58_support.py or tests/acceptance/W1-27/w1_27_support.py) |
| the reader (S2) | `gov.retrieval.lexical.ids_in`, `ID_SHAPE`, `whole_id` (src/gov/retrieval/lexical.py, the public names only) |
| the stop (S3) | `gov retrieve` (`gov.retrieve.command.run`); the UNRESOLVED_IDS bundle's shape: tests/acceptance/W2-13/test_w2_13_stated_gap.py and tests/unit/retrieve/test_w2_13_stated_gap.py; a planted store: tests/acceptance/W2-13/w2_13_support.py |
| sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1071, DEC-1099, DEC-1098, DEC-1097, DEC-900 |

Search with Read, Grep and Glob; if the first search does not answer, search once more in other words (DEC-1065).

## What to test (one or more cases per line; name the KPI id in each test's name or docstring)
- **S1 / F3 (schema)**: validate with `jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())`
  (Interface 1). A valid planted path map plus `id_forms:` with two well-formed forms is accepted; `id_forms: []` is
  accepted; the same map with an entry with no `name`, one with no `pattern`, and one whose pattern does not compile
  (e.g. `"("`) is refused each time (one case per malformed entry); an empty-string pattern is refused.
- **S2 / F3 (reader)**: a planted `<tmp>/governance/project/path-map.yaml` holding only `id_forms`, read with
  `lexical.id_forms(tmp_root)` and passed as `ids_in(text, forms)`. Five planted forms the built-in shape does not read:
  no hyphen, lowercase, underscore, a dotted suffix, a space between prefix and number. Each: read when declared (whole,
  once, in order of position, beside the built-in shape's ids in the same text) and not read by `ids_in(text)` /
  `ids_in(text, ())`. A token of a declared form inside a longer word is not read (whole-token rule). Overlap: under a
  dotted form, `SPEC-4.2` is read whole, not `SPEC-4` beside it (Interface 3). Byte-identical: a planted text of
  today's built-in ids gives the same list from `ids_in(text)` and from `ids_in(text, forms)` when no declared form
  matches in it, and `ids_in(text)` equals the expression today's code runs (compare to
  `list(dict.fromkeys(n for n in ID_SHAPE.findall(text) if any(c.isdigit() for c in n)))`).
  `id_forms`: no file, no key, or `[]` gives `()`; a malformed entry (not a map, no name, no pattern, a pattern that does
  not compile) raises `GovError` with code `CONFIG_INVALID` naming `id_forms[<i>]`.
- **S3 / F1 / F2 (the stop, end to end)**: a planted store (as w2_13_support plants one) whose path map declares the
  forms. For each planted form: a question naming an id of that form that exists nowhere (no record, no line holds it
  as a whole token) gives `stopping_reason == "UNRESOLVED_IDS"`, `evidence == []`, a gap `{"id": <the id>, "reason":
  "UNRESOLVED"}`, `continuation` null (F1: any evidence there is the failure). The same id present as a whole token on
  one line of an indexed file is retrieved: `stopping_reason != "UNRESOLVED_IDS"` and the output never prints
  UNRESOLVED_IDS for it (F2). The "every" rule: a question naming one nonexistent declared-form id and one id that
  exists is retrieved as before. The `--id <declared-form id>` path is checked too (Interface 4). A malformed form in
  the store's path map makes `gov retrieve` fail with `CONFIG_INVALID` (exit 1), before any search (Interface 5).
- **S4**: with no form declared, a question naming a nonexistent built-in-shape id still stops as today, and one
  naming a declared-form-like token (e.g. lowercase) with no forms declared does not stop on it. The existing suites
  are the lead's to run; do not copy them.

## Rules
- Plant everything in `tmp_path`; never this repository's store, `~/gov-os-runs`, or W2-00-store. No question, label
  or id from a hidden or spent evaluation set: invent your own (e.g. `req12`, `TKT_7`, `ZQ 41`, `ABC9`, `SPEC-4.2`).
- Build no embeddings and call no model: if the planted store's semantic facet is unavailable, the tests still hold
  (the stop and the lexical route do not need it); mark nothing `real`, `green_here`, `time_limit` or `local_only`.
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside ~/gov-os-runs,
  `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, as one line:
  `mkdir -p /tmp/w2-146-td && env TMPDIR=/tmp/w2-146-td HOME=/home/usain/gov-os-worktrees/W2-146-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-146-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-146 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Expected now: collection succeeds, and every KPI's tests are red for the missing behaviour (an ImportError of
  `id_forms` inside a test is fine; a collection error of the whole folder is not: import inside the tests or guard
  the import). Report the summary line and which tests are red and why.
- Commit your paths only, in one or two batches:
  `git commit -m "<subject>" --trailer "Task: DAEO-f6x3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1071, DEC-1099" -- tests/acceptance/W2-146`
  (`Implements:` only ids from the ticket's `sources:`: DEC-1071, DEC-1099, DEC-1098, DEC-1097, DEC-900.)
  `git status --short` empty when you return.
- One-line commands only; anything longer goes in a file under `.gov-runtime/scratch/td/` run with `bash` or
  `python3`. Literal paths. Never touch `src/`, `template/`, `.gov-runtime/scratch/lead/` or `.claude/`. No install, no
  network. Do not change the Interface: a gap or contradiction in it comes back as a package (question, options with
  cost, recommendation) in your return, with the tests you could write.

## The ticket's context packet (gov context DAEO-f6x3 --role independent-test-designer)
