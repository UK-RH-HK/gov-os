## The interface (the ticket's "Interface" section, plus the lead's decisions where it is silent; the same text goes to the test designer and the engineer)

From the ticket (read it in full):
- `src/gov/adopt/verify_pass.py`: `missing(root) -> list[{"ticket": <id>, "labels": [<label>, ...]}]`;
  `apply(root, answers_path, session, today) -> list[str]` (the ids of the tickets changed). Both read KPI lines with
  `gov.brief.build.kpi_rows` (imported, never changed). Errors are `gov.cli.errors.GovError` with codes
  `VERIFY_PASS_UNKNOWN_TICKET`, `VERIFY_PASS_CLOSED`, `VERIFY_PASS_UNKNOWN_LABEL`, `VERIFY_PASS_UNANSWERED`,
  `VERIFY_PASS_EMPTY_CLAUSE`.
- Flags on `gov adopt` (no `--lite` needed): `--verify-list`, `--verify-apply <answers-file>`; `--root` is gov's global flag.
- Answers file (YAML, outside the repository): `{<ticket id>: {S1: "<clause>", F2: "<clause>"}}`.
- Marker: one front-matter line `verify_pass: <YYYY-MM-DD> <session>`, added just before the closing `---`.
- A KPI line given as a plain string gets ` Verify: <clause>` appended; a `{line, verify}` mapping is never edited.

The lead's decisions (L1-L9; DEC-1157 lets the lead state these at the start):
- L1 `--verify-list` output: gov's usual result dict, `{"missing": [{"ticket": "<id>", "labels": ["S2", "F1"]}, ...],
  "text": "<lines>"}`; `text` is one line per ticket, `<id> <label> <label>...`, tickets sorted by id, labels in
  `kpi_rows` order; when no ticket lacks a verify, `missing` is `[]` and `text` is exactly `none`. Exit 0 in both cases.
  Listed: tickets whose front-matter `status` is `open` or `in_progress`. The id is the front-matter `id`.
- L2 `--verify-apply` result: `{"changed": [<id>, ...]}` (sorted), exit 0. A refusal is a `GovError` (gov's exit 1,
  the code on stderr, or in the envelope with `--json`), and nothing is written anywhere.
- L3 the marker's `<session>` is gov's global `--session` value (`args.session`, default `""`); `--verify-apply`
  without a non-empty `--session` is a usage error (argparse's, exit 2), nothing written; `<date>` is the UTC date of the run
  (`today` in the function). If the ticket already carries a `verify_pass:` line, that line's value is replaced in place
  (still exactly one such line).
- L4 checks, all before any write, over every entry: an answers key that is no ticket id under `.tickets/` ->
  `VERIFY_PASS_UNKNOWN_TICKET`; a ticket with `status: closed` -> `VERIFY_PASS_CLOSED`; a label that is not one of the
  ticket's lines lacking a verify (no such S<n>/F<n>, or that line already has a verify) -> `VERIFY_PASS_UNKNOWN_LABEL`;
  a named ticket with a line lacking a verify that the file does not answer -> `VERIFY_PASS_UNANSWERED`; a clause that
  is not a string, is empty or whitespace, or is only TBD, TODO, n/a or none (any case, ignoring surrounding whitespace
  and trailing `.`) -> `VERIFY_PASS_EMPTY_CLAUSE`. An answers file missing, not YAML, or not a mapping of mappings ->
  `VERIFY_PASS_ANSWERS_UNREADABLE`.
- L5 the edit is text-only (no YAML dump). The clause is appended inside the scalar: a plain scalar gets
  ` Verify: <clause>` at its end; a single- or double-quoted scalar gets it inside its quotes, escaped for that style.
  Where a plain scalar cannot hold the clause (for example the clause holds `: ` or ` #`), that one item may be turned
  into a single-quoted scalar (that item's bytes only). After editing in memory, the tool re-reads each edited ticket
  with the same loader and checks that `kpi_rows` gives each answered label exactly its clause and every other
  front-matter value is unchanged; otherwise it refuses with `VERIFY_PASS_EDIT_FAILED` and writes nothing. A block or
  folded scalar the tool cannot extend is refused the same way.
- L6 the facts step (S5): `gov adopt --facts --root <repo>` (no `--lite` needed) calls
  `gov.adopt.facts.write_default(root: Path, today: datetime.date) -> {"path": "<repo>/governance/project/facts.yaml",
  "written": true|false}`; the command passes the UTC date of the run. With no facts file it writes one; with one it
  writes nothing (`written: false`), the file byte-identical.
- L7 the facts file written: validates against `template/governance/kernel/schemas/facts.schema.json`;
  `ready.new_since` is `today` as a quoted ISO string (`'2026-11-13'`); every other value is a product default, with no
  path or name of the repository it is written into (the commands are `gov ...` forms). `wait_for` is
  `gov wait {EXIT_FILE}` (check `gov wait --help`): `gov wait` is on this base (caf96ed0f). A command with no product
  form is a named placeholder: its `run` (and `check`) is `{UNSET_<NAME>}` with `<NAME>` the command's name upper-cased,
  so `lead_verify` is `{UNSET_LEAD_VERIFY}`, and `gov brief` refuses it as `PLACEHOLDER_LEFT` naming `UNSET_LEAD_VERIFY`
  for any role whose template names `{CMD:lead_verify}` (the lead's). Whether `launch_worker` has a product form
  (`gov launch`) is the engineer's call; tests check only that each command's `run` starts with `gov ` or is exactly
  `{UNSET_<NAME>}`, that `lead_verify` is `{UNSET_LEAD_VERIFY}` and that `wait_for` starts with `gov wait`.
- L8 scope (F3): `verify_pass.py` opens nothing outside `<root>/.tickets/` and the answers file; it imports no network
  or model package (no `socket`, `http`, `urllib`, `requests`, `httpx`, `anthropic`, `openai`, `subprocess`). The facts
  step is not the verify pass (the ticket's "Widened by the owner" section).
- L9 untouched: nothing under `src/gov/brief/`, `template/governance/kernel/templates/` or
  `template/governance/kernel/schemas/` changes; no adoption stage changes (`src/gov/adopt/stages.py` stays as it is).
