# Brief: engineer, W2-174 (DAEO-zmo4), run 1 batch 1: the verify pass (list, checks, apply), the facts step, their unit cases

You are a fresh engineer (role engineer), ticket DAEO-zmo4 (W2-174), profile STANDARD, class C2. Headless: only your last
message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-174 |
| branch | w2/W2-174 (from f2b1d38af) |
| your context packet (gov context output, JSON: the ticket, KPIs, sources) | /home/usain/gov-os-worktrees/W2-174/.gov-runtime/scratch/brief/en-context.md |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-zmo4.md |
| the approach (why option (d)) | /home/usain/gov-os-worktrees/W2-174/governance/project/orchestration/packages/ADOPT-VERIFY-1/APPROACH.md |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-174/docs/DECISION_REGISTER.md |
| scratch | your sandbox's own `$TMPDIR` only (`/tmp` is read-only in the sandbox) |

Your allowed paths (write nothing else):
- `src/gov/adopt/verify_pass.py` (new)
- `src/gov/adopt/command.py` (the flags `--verify-list`, `--verify-apply`, `--facts`, and their dispatch before the
  `--lite` check)
- `src/gov/adopt/facts.py` (new; see the warning below)
- `tests/unit/adopt/test_w2_174_*.py` (new: the unit cases the KPI lines' Verify clauses name: `test_w2_174_list.py`,
  `_apply.py`, `_ready.py`, `_checks.py`, `_facts.py`, `_scope.py`)

NOT `tests/acceptance/**` (a test designer writes `tests/acceptance/W2-174/` in `/home/usain/gov-os-worktrees/W2-174-tests`
at the same time: never read that tree or its branch, DEC-820; the lead merges its cases into your branch between your
batches). NOT `src/gov/brief/**`, `template/governance/kernel/**` or `src/gov/adopt/stages.py` (F2 and the ticket's
rabbit holes; the adopt skill's text is W2-88a's). If you find you need any of them, stop and say so in your return.

**Warning (known ticket defect).** The ticket's `allowed_paths` line for `src/gov/adopt/facts.py` carries an inline YAML
comment, and the guard reads that line raw (`gov.guard.decide._load_ticket` gives
`"src/gov/adopt/facts.py  # the adoption's facts file ..."`), so a write to `src/gov/adopt/facts.py` may be refused.
Build the verify pass first (S1-S4, F1, F3) and commit it. Then try to write `facts.py` once. If the guard refuses it,
do NOT put the facts code anywhere else (no work-around): write S5's unit cases in `test_w2_174_facts.py` if you can,
commit what you have, and report the refusal word for word; the CTO fixes the ticket line and the lead resumes you.

## Read first
- The ticket in full: its eight KPI lines (S1-S5, F1-F3), Interface, Rabbit holes, and the two owner sections at the end.
- `src/gov/brief/build.py` (read only): `Tickets`, `kpi_rows` (~109), `VERIFY`, `ready_check` (~163), `build` (~317),
  `Filler` (~186: how `{UNSET_...}` in a command's `run` becomes a `PLACEHOLDER_LEFT` finding).
- `src/gov/adopt/command.py` and `src/gov/cli/main.py` (the command-module convention: `add_arguments`, `run`, result
  dicts, `GovError`, the global `--root` and `--session`).
- `template/governance/kernel/schemas/facts.schema.json`, `governance/project/facts.yaml` (this repository's, as the
  shape only: no value of it goes into the defaults), `src/gov/wait/command.py`, `src/gov/launch/` (for a product form
  of `launch_worker`, if one fits).

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

## The work
1. Write the unit cases first (test-driven), on fixture repositories in `tmp_path`, matching each Verify clause:
   list (three tickets -> exactly the second ticket's two labels; all-verified -> `none`); apply (a ticket with YAML
   comments and five lines -> byte diff shows only the appended clauses and the one marker line); ready (`ready_check`
   finds no `KPI_NO_VERIFY` after apply; `gov brief engineer <ticket> --root <fixture>` exits 0 with the fixture's own
   filled facts file and the kernel templates copied in); checks (one case per refusal code, nothing written; nine good
   entries and one bad leave the tree byte-identical; one line unanswered is refused and unmarked); facts (validates
   against the kernel schema, `new_since` the step's date as a quoted string, `gov brief` no longer answers
   `BRIEF_FACTS_MISSING` and names the placeholders; an existing facts file byte-identical); scope (a decoy outside
   `.tickets/` byte-identical after list and apply; `verify_pass.py` imports no network or model package).
2. Implement `verify_pass.py` (all checks before any write; write all edited files only after every check and every
   re-read of L5 passed; write each file whole, by a temporary file in the same folder and a rename), the flags in
   `command.py`, and `facts.py`. Keep it small: the ticket's estimate is 180 lines of code.
3. Run your unit cases and `tests/unit/adopt/` as a whole, and `tests/acceptance/W2-152` (it must stay green unchanged),
   and quote their count lines.

## How you run tests
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-174/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-174/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder>[::<test>] -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"`. A resource gate's
refusal is a wait (relaunch when it opens). No skip, xfail, flaky or rerun mark.

## Searching
Read and Grep only; no `gov retrieve` or `gov context` in the sandbox. Search once, then once more in other words; answer
from what you read with path and line, or say "not found". Never open the evaluation sets' root, held-out material or any
hidden or memory-verdict folder.

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line of shell goes in a script
under your `$TMPDIR`, run with `bash <file>`. Refused twice for the same call by the guard, the sandbox or a hook: stop and
say so; never work around a refusal. No merge, no push.

## Commit (your paths only; commit after each working batch)
```
git -C /home/usain/gov-os-worktrees/W2-174 commit -m "<subject>" --trailer "Task: DAEO-zmo4" --trailer "Role: engineer" --trailer "Implements: DEC-1130, DEC-1083, DEC-1050, DEC-1088, DEC-1121, DEC-1122" -- <your paths>
```
Trailers in one final paragraph. Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; lines of code added (src only); any place where the ticket or
the interface above was unclear and how you read it; guard_refusals: none or a line each (word for word).
