# Brief eng-1: engineer for DAEO-f6x3 (W2-146), profile STANDARD, class C2

You implement ticket DAEO-f6x3 (W2-146): the id reader reads every id form a repository declares in its path map, so a
question naming a nonexistent id of a declared form stops with UNRESOLVED_IDS (DEC-1071 (5), DEC-1099 (2)). An
independent test designer writes the acceptance tests (tests/acceptance/W2-146/) in parallel; you never read them (the
guard refuses the counterpart's work). Write your own unit tests as you go (test first). Build exactly the ticket's
`## Interface` (P-W2-146-1 (a), accepted by the CTO); do not change it: a gap or contradiction comes back as a package
(question, options with cost, recommendation) in your return.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-146 |
| branch | w2/W2-146 |
| allowed paths | src/gov/retrieval/lexical.py, src/gov/retrieve/command.py, template/governance/kernel/schemas/path-map.schema.json, tests/unit/retrieval/test_w2_146*, tests/unit/retrieve/test_w2_146*, docs/changes/W2-146-evidence.md |
| ticket (read it first: S1-S4, F1-F3, and the `## Interface` at its end, binding) | /home/usain/gov-os-worktrees/W2-146/.tickets/DAEO-f6x3.md |
| the reader | src/gov/retrieval/lexical.py: `ID_SHAPE` (line ~82), `kept_out` (~153, the precedent for reading the path map with `read_yaml`), `ids_in` (~187), `whole_id` (~192); the other `ids_in(...)` callers (`_lead_id`, `search` ~519/567, `ID_SHAPE.sub`) stay as they are |
| the stop | src/gov/retrieve/command.py: `_nowhere` (~50), `_stated_gap` (~79), `run` (~114) |
| other callers that must not move | Grep `ids_in(` under src/gov (e.g. gov.memaudit.preflight); `gov.links` has its own `ids_in` (src/gov/links/check.py): not touched |
| the schema | template/governance/kernel/schemas/path-map.schema.json (draft 2020-12; `$defs/text` exists); src/gov/config/loader.py is NOT in your paths and is not changed |
| the existing tests that must pass unchanged (S4) | tests/unit/retrieval/, tests/unit/retrieve/, tests/acceptance/W2-13/, W1-20/, W1-21/, W2-138/ (those holding UNRESOLVED_IDS cases and the lexical route) |
| sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1071, DEC-1099, DEC-1098, DEC-1097, DEC-900 |

Search with Read, Grep and Glob; if the first search does not answer, search once more in other words (DEC-1065).

## What to build (the Interface, in short; the ticket's text governs)
1. Schema: optional top-level `id_forms`: array of `$defs/id_form` = object, `additionalProperties: false`, required
   `name` (`$ref: #/$defs/text`) and `pattern` (string, minLength 1, `format: regex`). Nothing else in the schema moves;
   keep the file's formatting style. Report the file's sha256 before (7a1a1cd8cbf6fb073e2e1eb6f816d2ba83e2b647e2dc94efb1dfa96f359a8469)
   and after, and the lines added, in docs/changes/W2-146-evidence.md (the lead writes the CIT-P record from it).
2. `lexical.id_forms(root) -> tuple[re.Pattern, ...]`: reads only `id_forms` of `<root>/governance/project/path-map.yaml`
   with `read_yaml` (as `kept_out` does). No file, no key, `[]`: `()`. An entry not a map, without a non-empty string
   `name` or `pattern`, or whose pattern does not compile: `GovError("CONFIG_INVALID", ...)` naming `id_forms[<i>]` and
   the reason. Compiled with no flags.
3. `ids_in(text: str, forms: Sequence[re.Pattern] = ()) -> list[str]`: `forms=()` runs today's expression unchanged
   (byte-identical). With forms: candidates are the built-in shape's matches holding a digit plus each form's
   `finditer` `group(0)`, a form's match kept only when non-empty and a whole token by `whole_id`'s rule checked at the
   match's span (no word char or `-` before; after, no word char and no `-` followed by a word char). Overlaps: sorted
   by start, longest first; a candidate overlapping one kept is dropped. Then each text once, in position order.
4. Only `_nowhere` passes forms: `forms = lexical.id_forms(root)` once (the store root it is given), then
   `ids_in(..., forms)` for the question and for the `--id`/ticket check (`ids_in(name, forms) != [name]`). The rest of
   `_nowhere` and `_stated_gap` unchanged. Mind that `_nowhere` returns None on `GovError` from the records check only:
   a `CONFIG_INVALID` from `id_forms` must propagate (gov retrieve exits 1 with it, before any search), not be swallowed.
5. Check end to end that the stop's existing per-name search (`lexical.search(root, name, refresh=False)` + `whole_id`)
   finds a declared-form id present as a whole token on one line, for each form kind, including one with a space
   (`ZQ 41`) and a lowercase one: if `lexical.search` cannot find such a line by that query (the FTS query form), the
   stop would fire on an id that exists (F2): report that as a package with options rather than widening the change
   outside the Interface.

## Your unit tests (tests/unit/retrieval/test_w2_146_*.py, tests/unit/retrieve/test_w2_146_*.py)
Cover: the schema (two forms accepted; nameless, patternless, non-compiling, empty pattern refused, with
`Draft202012Validator(schema, format_checker=FormatChecker())`); `id_forms` (no file, no key, `[]`, each malformed
entry -> CONFIG_INVALID naming the index); `ids_in` for five planted kinds (no hyphen, lowercase, underscore, dotted
suffix, space between prefix and number), read when declared and not when not, whole-token, overlap (`SPEC-4.2` whole),
byte-identical with `forms=()`; `_nowhere`/`run` on a planted store (see tests/acceptance/W2-13/w2_13_support.py for
how one is planted, and tests/unit/retrieve/test_w2_13_stated_gap.py) for a nonexistent and an existing declared-form
id, the "every" rule, and CONFIG_INVALID. Invent your ids; plant in `tmp_path`; never this repository's store,
~/gov-os-runs or W2-00-store; no model, no embeddings.

## Rules
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside ~/gov-os-runs,
  `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, one folder per run,
  as one line:
  `mkdir -p /tmp/w2-146-eng && env TMPDIR=/tmp/w2-146-eng HOME=/home/usain/gov-os-worktrees/W2-146/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-146/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/retrieval -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  End with tests/unit/retrieval and tests/unit/retrieve green, and run once each of tests/acceptance/W2-13,
  tests/acceptance/W1-20, tests/acceptance/W1-21 and tests/acceptance/W2-138 the same way: report their summary lines.
  A red there that also fails on the merge base (w2/integrate's head) is a shared base red: name it with that
  evidence, not yours to fix.
- Commit in batches (schema + reader; the stop; the evidence record), your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-f6x3" --trailer "Role: engineer" --trailer "Implements: DEC-1071, DEC-1099" -- <your paths>`
  (`Implements:` only ids from the ticket's `sources:`: DEC-1071, DEC-1099, DEC-1098, DEC-1097, DEC-900; name the ones
  each commit carries.) The lead may merge the acceptance tests into your branch between your batches: commit before a
  long pause, and `git status --short` empty when you return.
- One-line commands only; a longer script goes in a file under `.gov-runtime/scratch/eng/` run with `bash` or
  `python3`. Use literal paths. Never touch `.gov-runtime/scratch/lead/`, `.gov-runtime/scratch/briefs/` or
  `tests/acceptance/`. No install, no network, no `.claude/`.

## The ticket's context packet (gov context DAEO-f6x3 --role engineer)
